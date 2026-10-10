"""Offline admission candidate. Trusted inputs must come from the host.

This module authenticates nobody, queries no stores and ranks no candidates.
It validates an untrusted reuse result against an immutable supplied snapshot.
"""
from copy import deepcopy
import json
from dataclasses import dataclass
from types import MappingProxyType


class Refused(ValueError):
    pass


BINDING_FIELDS = frozenset({
    'request_id', 'need_revision', 'need_digest', 'catalogue_digest',
    'policy_revision', 'rule_version',
})
ALERT_FIELDS = frozenset({
    'kind', 'binding', 'need_id', 'offer_id', 'provider_id', 'target_kind',
    'locator', 'artifact_digest', 'contract_fit', 'evidence_refs',
    'unresolved_conditions', 'rationale', 'suggested_next_step', 'authority',
})
BASES = frozenset({
    'declaration', 'advertisement', 'schema-valid-completion',
    'accepted-performance', 'review-verdict',
})


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _binding(value):
    if not isinstance(value, dict) or set(value) != BINDING_FIELDS:
        raise Refused('invalid_binding')
    if type(value['need_revision']) is not int or value['need_revision'] < 1:
        raise Refused('invalid_revision')
    if not all(_nonempty(value[k]) for k in BINDING_FIELDS - {'need_revision'}):
        raise Refused('invalid_binding')


@dataclass(frozen=True)
class Admitted:
    """Transport admission only. Application acceptance is a separate step."""
    result: dict
    transport: str = 'validated'
    acceptance: str = 'pending'
    execution_authorized: bool = False


class ReuseAdmission:
    def __init__(self, *, binding, need_id, visible_offers, evidence,
                 host_candidates, required_conditions=(), max_text=4000,
                 max_refs=32):
        """All arguments are trusted synthetic inputs, not model output.

        visible_offers: host-filtered offer records keyed by id.
        evidence: host-resolved records keyed by id, including custody and
        applicability decisions on the exact artifact/context.
        host_candidates: existing matcher witnesses keyed by offer id, with
        fit, uncertainty and hard-requirement contradiction fields.
        """
        _binding(binding)
        if not _nonempty(need_id):
            raise Refused('invalid_need')
        if type(max_text) is not int or max_text < 1 or type(max_refs) is not int or max_refs < 1:
            raise Refused('invalid_limits')
        self.__snapshot = deepcopy({
            'binding': binding, 'need_id': need_id, 'offers': visible_offers,
            'evidence': evidence, 'candidates': host_candidates,
            'required_conditions': tuple(required_conditions),
        })
        self.__limits = MappingProxyType({'text': max_text, 'refs': max_refs})

    def admit(self, output, *, current_binding, active=True):
        """Current lifecycle/revision must be resolved afresh by the host."""
        try:
            encoded = json.dumps(output, allow_nan=False)
        except (TypeError, ValueError, RecursionError) as exc:
            raise Refused('invalid_json_result') from exc
        if len(encoded.encode('utf-8')) > 32768:
            raise Refused('result_too_large')
        try:
            return self._admit(output, current_binding=current_binding, active=active)
        except (TypeError, KeyError, RecursionError) as exc:
            raise Refused('malformed_result_or_host_snapshot') from exc

    def _admit(self, output, *, current_binding, active):
        if active is not True:
            raise Refused('request_inactive')
        _binding(current_binding)
        snapshot = self.__snapshot
        if current_binding != snapshot['binding']:
            raise Refused('stale_snapshot')
        if not isinstance(output, dict) or set(output) != ALERT_FIELDS:
            raise Refused('invalid_result_fields')
        result = deepcopy(output)
        _binding(result['binding'])
        if result['binding'] != snapshot['binding']:
            raise Refused('binding_mismatch')
        if result['kind'] != 'reuse-alert' or result['authority'] != 'recommendation-only':
            raise Refused('recommendation_only')
        if result['need_id'] != snapshot['need_id']:
            raise Refused('need_mismatch')
        if not _nonempty(result['offer_id']):
            raise Refused('invalid_offer')
        offer = snapshot['offers'].get(result['offer_id'])
        candidate = snapshot['candidates'].get(result['offer_id'])
        # Generic refusal avoids disclosing whether a hidden offer exists.
        if offer is None or candidate is None:
            raise Refused('offer_unavailable')
        for field in ('provider_id', 'target_kind', 'locator', 'artifact_digest'):
            if result[field] != offer[field]:
                raise Refused('offer_binding_mismatch')
        if offer['target_kind'] not in {'code', 'service'}:
            raise Refused('invalid_target_kind')
        locator = result['locator']
        locator_fields = {'code': {'workspace', 'symbol'}, 'service': {'service'}}[offer['target_kind']]
        if (not isinstance(locator, dict) or set(locator) != locator_fields
                or not all(_nonempty(locator[key]) for key in locator_fields)):
            raise Refused('invalid_target_locator')
        expected_next = {'code': {'inspect-existing-code'},
                         'service': {'ask-existing-service', 'consider-connection'}}
        if result['suggested_next_step'] not in expected_next[offer['target_kind']]:
            raise Refused('invalid_next_step')
        if candidate.get('hard_requirement_contradicted'):
            raise Refused('hard_requirement_contradicted')
        fit = candidate['contract_fit']
        if fit not in {'supported', 'possible', 'conflicting'} or result['contract_fit'] != fit:
            raise Refused('fit_overclaim')
        unresolved = result['unresolved_conditions']
        if not isinstance(unresolved, list) or not all(_nonempty(x) for x in unresolved):
            raise Refused('invalid_uncertainty')
        if len(unresolved) != len(set(unresolved)):
            raise Refused('duplicate_uncertainty')
        required = set(candidate['unresolved_conditions']) | set(snapshot['required_conditions'])
        if not required.issubset(set(unresolved)):
            raise Refused('uncertainty_erased')
        if required and fit == 'supported':
            raise Refused('unresolved_fit')
        if not _nonempty(result['rationale']) or len(result['rationale']) > self.__limits['text']:
            raise Refused('invalid_rationale')
        refs = result['evidence_refs']
        if not isinstance(refs, list) or not 1 <= len(refs) <= self.__limits['refs']:
            raise Refused('invalid_evidence_refs')
        seen = set()
        for reference in refs:
            if not isinstance(reference, dict) or not _nonempty(reference.get('id')):
                raise Refused('invalid_evidence_ref')
            if reference['id'] in seen:
                raise Refused('duplicate_evidence')
            seen.add(reference['id'])
            record = snapshot['evidence'].get(reference['id'])
            if record is None or reference != record['reference']:
                raise Refused('evidence_unavailable_or_changed')
            if record['offer_id'] != result['offer_id']:
                raise Refused('foreign_evidence')
            if record['artifact_digest'] != result['artifact_digest']:
                raise Refused('artifact_evidence_mismatch')
            if record.get('custody_verified') is not True or record.get('applicable') is not True:
                raise Refused('evidence_not_qualified')
            if reference.get('basis') not in BASES:
                raise Refused('invalid_evidence_basis')
            if reference['basis'] == 'review-verdict':
                if not all(_nonempty(reference.get(k)) for k in ('verdict', 'mandate', 'origin_id')):
                    raise Refused('review_missing_context')
        # Required evidence includes adverse or conflicting evidence selected
        # by the host; model output cannot cherry-pick it out of the result.
        if not set(candidate['required_evidence_ids']).issubset(seen):
            raise Refused('required_evidence_omitted')
        return Admitted(result)


TYPED_NEED_FIELDS = frozenset({
    'kind','binding','operation','inputs','required_outputs','hard_constraints',
    'preferences','prerequisites','assumptions','unknowns','alternatives',
    'source_refs','interpretation_status',
})
NO_CANDIDATE_FIELDS = frozenset({
    'kind','binding','need_id','searched_scope','unknowns','search_complete','truncation_reason',
})


def _bound_result(output, fields, binding, current_binding, active):
    _binding(binding)
    _binding(current_binding)
    if active is not True:
        raise Refused('request_inactive')
    if binding != current_binding:
        raise Refused('stale_snapshot')
    if not isinstance(output,dict) or set(output) != fields:
        raise Refused('invalid_result_fields')
    try:
        encoded=json.dumps(output,allow_nan=False)
    except (TypeError,ValueError,RecursionError) as exc:
        raise Refused('invalid_json_result') from exc
    if len(encoded.encode('utf-8')) > 32768:
        raise Refused('result_too_large')
    _binding(output['binding'])
    if output['binding'] != binding:
        raise Refused('binding_mismatch')


def _strings(value, *, required=False):
    if (not isinstance(value,list) or len(value)>64
            or not all(_nonempty(x) and len(x)<=1024 for x in value)
            or len(value)!=len(set(value)) or (required and not value)):
        raise Refused('invalid_text_list')


def admit_typed_need(output, *, binding, current_binding, source_need,
                     known_operations, active=True):
    """Offline proposed interpretation; trusted source context supplied by host.

    The source_need is normalized by the requester/host, not generated by Match.
    Known operations come from the visible host catalogue. Structural admission
    does not assess semantic quality of the interpretation or approve a plan.
    """
    _bound_result(output,TYPED_NEED_FIELDS,binding,current_binding,active)
    if output['kind']!='typed-need' or output['interpretation_status']!='proposed':
        raise Refused('interpretation_not_proposed')
    if not _nonempty(output['operation']) or output['operation'] not in known_operations:
        raise Refused('operation_not_in_visible_catalogue')
    for key in ('inputs','required_outputs','prerequisites','assumptions','unknowns','alternatives'):
        _strings(output[key],required=key in {'inputs','required_outputs'})
    # Preserve explicit source constraints verbatim. New inferred conditions
    # belong to assumptions/unknowns, never silently become hard requirements.
    for key in ('hard_constraints','preferences','source_refs'):
        if output[key] != source_need[key]:
            raise Refused('source_constraints_or_provenance_changed')
    if not set(source_need.get('unknowns',[])).issubset(set(output['unknowns'])):
        raise Refused('uncertainty_erased')
    return Admitted(deepcopy(output))


def admit_no_candidate(output, *, binding, current_binding, need_id,
                       search_receipt, active=True):
    """Host-derived search receipt, not Match's own claim of global absence."""
    _bound_result(output,NO_CANDIDATE_FIELDS,binding,current_binding,active)
    if output['kind']!='no-candidate' or output['need_id']!=need_id:
        raise Refused('need_mismatch')
    if search_receipt['candidate_count'] != 0:
        raise Refused('candidates_exist')
    if output['searched_scope']!=search_receipt['searched_scope']:
        raise Refused('search_scope_changed')
    if type(output['search_complete']) is not bool or output['search_complete'] is not search_receipt['search_complete']:
        raise Refused('search_completion_overclaim')
    if output['truncation_reason']!=search_receipt['truncation_reason']:
        raise Refused('truncation_changed')
    if output['search_complete'] and output['truncation_reason'] is not None:
        raise Refused('inconsistent_search_receipt')
    if not output['search_complete'] and not _nonempty(output['truncation_reason']):
        raise Refused('inconsistent_search_receipt')
    _strings(output['unknowns'])
    if not set(search_receipt['unknowns']).issubset(set(output['unknowns'])):
        raise Refused('uncertainty_erased')
    return Admitted(deepcopy(output))
