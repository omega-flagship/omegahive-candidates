"""Proposed inert role revision after theory review. No live or host state changes."""
import copy
import hashlib
import json
from omegaalignment.swarm import blueprint

ORIENTATION = (
    "Keep operator adoption, the subject's authenticated endorsement stance, and "
    "affected-party standing separate. Never infer one from another or record "
    "endorsement for the subject. Bind their exact revisions, scope, governing "
    "interval and interpretation when host records exist. Missing records stay "
    "explicit gaps; an operator baseline alone cannot establish the subject's "
    "own values. Preserve conflicts and route them to legitimate governance. "
    "Separate task-TTL working notes from durable scoped episode lineage. "
    "A saved file, familiar name or identical prompt does not establish identity "
    "or commitment continuity. Record predictions, decision/action bindings, "
    "independent outcomes, correction identities and appeals only through "
    "available granted host facilities. No facility means a gap, not a shadow "
    "adoption registry. Unknown guides a bounded resolving question, not endless "
    "inquiry or automatic rejection of every action. "
)
PROCEDURES = {
    'drift': (
        "Identify whether change concerns belief, interpretation, implementation, "
        "behavior, commitment or identity continuity. Empirical learning and "
        "better realization can preserve a commitment; a stable commitment may "
        "still cause harm. Digest equality identifies bytes, not meaning. When "
        "meaning changes, retain the earlier interpretation and the mapping "
        "claim. Pass Flourishing the exact unresolved change and evidence "
        "question; preserve its answer or disagreement without averaging it. "
    ),
    'flourishing': (
        "For each admitted alternative and represented being, expose the "
        "source-bound appraisal over all nine retained pattern obligations, "
        "coverage, horizon, predicted versus observed status, provenance and "
        "protected-floor concerns. Use the actually granted native appraisal "
        "interface and report its source/interpreter/interpretation pins. "
        "Do not claim native appraisal from prose or an unavailable skill. "
        "Retained law permits equal comparable statuses and supports over "
        "undermines; neutral is not an intermediate rank, and unknown/tension "
        "are incomparable. No hidden scalar tie-breaker. An incomparable result "
        "routes to inquiry, deliberation or separately authorized choice. "
        "Ask Drift whether an unexpected impact reflects a changed commitment, "
        "implementation or world model. Consider beneficial opportunity, "
        "exploration and assessor burden as well as harm. "
    ),
    'coordinator': (
        "Assemble a decision packet retaining exact independent receipts, "
        "coverage gaps, incomparable alternatives and dissent. Route specific "
        "intermediate questions between mandates so they can help resolve an "
        "impasse; do not substitute a vote or your ranking for native appraisal. "
        "Bind pre-review and post-review choices and independent consequences "
        "when granted records exist. Report useful contribution, missed risks "
        "and added burden without claiming causal influence from timing alone. "
        "Alignment's own method changes require independent scrutiny, not "
        "self-certification. A receipt is evidence of bounded review only. "
    ),
}

def proposal():
    original = blueprint()
    value = copy.deepcopy(original)
    value.pop('configuration_digest')
    for role in value['roles']:
        fields = role['fields']
        fields['name'] = fields['name'].removesuffix(' v1') + ' v2 proposal'
        if fields['mandate']:
            fields['mandate']['version'] = '2'
        fields['prompt'] += ORIENTATION + PROCEDURES[role['key']]
    value['requirements']['service'] = {'kind': 'review', 'connection_only_kinds': ['review'], 'public_kinds': []}
    value['requirements']['status'] = 'v2-proposal-unqualified'
    value['requirements']['host_contracts'] += [
        'authenticated-subject-endorsement', 'scoped-standing',
        'source-bound-native-appraisal-interface', 'durable-scoped-episode-lineage']
    value['revision_proposal'] = {
        'predecessor_configuration_digest': original['configuration_digest'],
        'adopted': False, 'activated': False,
        'reason': 'Theory review: legitimacy, native appraisal, longitudinal memory and reciprocal inquiry gaps',
        'service_contract': {'kinds': [], 'connection_only_kinds': ['review']},
        'claim_ceiling': 'Prepared role proposal only; no runtime skills, host records or cognition supplied'}
    digest = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
    return dict(value, configuration_digest=digest)

if __name__ == '__main__':
    print(json.dumps(proposal(), indent=2, ensure_ascii=False))
