from copy import deepcopy
import pytest
from omegamatch.protocol import ReuseAdmission, Refused


def fixture():
    binding = dict(request_id='request-1', need_revision=1, need_digest='need-v1',
                   catalogue_digest='catalogue-v1', policy_revision='policy-v1', rule_version='rules-v1')
    offer = dict(provider_id='code:invented', target_kind='code',
                 locator={'workspace': 'synthetic/csv.py', 'symbol': 'parse_rows'}, artifact_digest='tree-v1')
    ref = dict(id='e1', digest='evidence-v1', basis='advertisement',
               context='invented-csv-case', observed_at='2026-10-04', origin_id='run-1')
    evidence = {'e1': dict(reference=ref, offer_id='offer-1', artifact_digest='tree-v1',
                           custody_verified=True, applicable=True)}
    candidate = dict(contract_fit='possible', unresolved_conditions=['performance unknown'],
                     required_evidence_ids=['e1'], hard_requirement_contradicted=False)
    inputs = dict(binding=binding, need_id='need-1', visible_offers={'offer-1':offer},
                  evidence=evidence, host_candidates={'offer-1':candidate})
    output = dict(kind='reuse-alert', binding=deepcopy(binding), need_id='need-1', offer_id='offer-1',
                  **deepcopy(offer), contract_fit='possible', evidence_refs=[deepcopy(ref)],
                  unresolved_conditions=['performance unknown'], rationale='Visible contract matches; performance unverified.',
                  suggested_next_step='inspect-existing-code', authority='recommendation-only')
    return inputs, output


def test_admission_is_pending_and_grants_nothing():
    inputs, output = fixture()
    admitted = ReuseAdmission(**inputs).admit(output, current_binding=inputs['binding'])
    assert admitted.transport == 'validated'
    assert admitted.acceptance == 'pending'
    assert admitted.execution_authorized is False
    output['locator']['symbol'] = 'mutated'
    assert admitted.result['locator']['symbol'] == 'parse_rows'


@pytest.mark.parametrize('field', ['need_revision','need_digest','catalogue_digest','policy_revision','rule_version'])
def test_current_change_invalidates_snapshot(field):
    inputs, output = fixture()
    current = deepcopy(inputs['binding'])
    current[field] = 2 if field == 'need_revision' else 'changed'
    with pytest.raises(Refused, match='stale_snapshot'):
        ReuseAdmission(**inputs).admit(output, current_binding=current)


@pytest.mark.parametrize('change,reason', [
    ({'authority':'dispatch'}, 'recommendation_only'),
    ({'execution_authorized':True}, 'invalid_result_fields'),
    ({'provider_id':'code:other'}, 'offer_binding_mismatch'),
    ({'artifact_digest':'tree-v2'}, 'offer_binding_mismatch'),
    ({'offer_id':'hidden'}, 'offer_unavailable'),
    ({'contract_fit':'supported'}, 'fit_overclaim'),
    ({'unresolved_conditions':[]}, 'uncertainty_erased'),
    ({'suggested_next_step':'execute'}, 'invalid_next_step'),
])
def test_untrusted_result_refusals(change, reason):
    inputs, output = fixture()
    output.update(change)
    with pytest.raises(Refused, match=reason):
        ReuseAdmission(**inputs).admit(output, current_binding=inputs['binding'])


@pytest.mark.parametrize('active', [False, None, 'true'])
def test_cancelled_or_unconfirmed_lifecycle_refused(active):
    inputs, output = fixture()
    with pytest.raises(Refused, match='request_inactive'):
        ReuseAdmission(**inputs).admit(output, current_binding=inputs['binding'], active=active)


def test_model_cannot_promote_evidence():
    inputs, output = fixture()
    output['evidence_refs'][0]['basis'] = 'accepted-performance'
    with pytest.raises(Refused, match='evidence_unavailable_or_changed'):
        ReuseAdmission(**inputs).admit(output, current_binding=inputs['binding'])


@pytest.mark.parametrize('field,value,reason', [
    ('artifact_digest','old-tree','artifact_evidence_mismatch'),
    ('offer_id','other-offer','foreign_evidence'),
    ('custody_verified',False,'evidence_not_qualified'),
    ('applicable',False,'evidence_not_qualified'),
])
def test_evidence_must_belong_to_current_offer_and_tree(field,value,reason):
    inputs, output = fixture()
    inputs['evidence']['e1'][field] = value
    with pytest.raises(Refused, match=reason):
        ReuseAdmission(**inputs).admit(output, current_binding=inputs['binding'])


def test_host_snapshot_survives_caller_mutation():
    inputs, output = fixture()
    admission = ReuseAdmission(**inputs)
    inputs['visible_offers']['offer-1']['artifact_digest'] = 'mutated'
    inputs['evidence']['e1']['reference']['basis'] = 'accepted-performance'
    assert admission.admit(output, current_binding=inputs['binding']).acceptance == 'pending'


def test_adverse_review_cannot_be_omitted_or_rewritten():
    inputs, output = fixture()
    adverse = dict(id='e2',digest='review-v1',basis='review-verdict',context='invented-csv-case',
                   observed_at='2026-10-04',verdict='rejected',mandate='correctness-v1',origin_id='run-2')
    inputs['evidence']['e2'] = dict(reference=adverse,offer_id='offer-1',artifact_digest='tree-v1',
                                   custody_verified=True,applicable=True)
    inputs['host_candidates']['offer-1'].update(contract_fit='conflicting',required_evidence_ids=['e1','e2'])
    output['contract_fit']='conflicting'
    admission=ReuseAdmission(**inputs)
    with pytest.raises(Refused, match='required_evidence_omitted'):
        admission.admit(output,current_binding=inputs['binding'])
    output['evidence_refs'].append(deepcopy(adverse))
    assert admission.admit(output,current_binding=inputs['binding']).acceptance == 'pending'
    output['evidence_refs'][1]['verdict']='accepted'
    with pytest.raises(Refused, match='evidence_unavailable_or_changed'):
        admission.admit(output,current_binding=inputs['binding'])


def test_hard_contradiction_is_not_an_eligible_alert():
    inputs, output = fixture()
    inputs['host_candidates']['offer-1']['hard_requirement_contradicted']=True
    with pytest.raises(Refused, match='hard_requirement_contradicted'):
        ReuseAdmission(**inputs).admit(output,current_binding=inputs['binding'])


def test_existing_service_alert_has_no_code_path_requirement():
    inputs, output = fixture()
    offer=dict(provider_id='swarm:planner',target_kind='service',locator={'service':'planning'},artifact_digest='service-v1')
    inputs['visible_offers']['offer-1']=offer
    inputs['evidence']['e1']['artifact_digest']='service-v1'
    output.update(**offer,suggested_next_step='ask-existing-service')
    assert ReuseAdmission(**inputs).admit(output,current_binding=inputs['binding']).execution_authorized is False


def test_duplicate_reports_cannot_be_counted_twice():
    inputs, output=fixture()
    output['evidence_refs'] *= 2
    with pytest.raises(Refused, match='duplicate_evidence'):
        ReuseAdmission(**inputs).admit(output,current_binding=inputs['binding'])


@pytest.mark.parametrize('field', ['suggested_next_step', 'contract_fit', 'offer_id'])
def test_malformed_fields_fail_cleanly(field):
    inputs, output=fixture()
    output[field]={'unexpected':'object'}
    with pytest.raises(Refused):
        ReuseAdmission(**inputs).admit(output,current_binding=inputs['binding'])


def test_large_result_is_bounded():
    inputs, output=fixture()
    output['unresolved_conditions'].append('x'*40000)
    with pytest.raises(Refused,match='result_too_large'):
        ReuseAdmission(**inputs).admit(output,current_binding=inputs['binding'])
