from copy import deepcopy
import pytest
from omegamatch.readiness import readiness_report, AXES


def context():
    return dict(requester='synthetic-requester', provider='synthetic-provider', generation='g2', skill='synthetic-skill',
                source_digest='source2', catalogue_digest='catalogue2', policy_revision='policy2')


def record(axis='loaded', stance='supported', ref='synthetic-ref'):
    return dict(context=context(), axis=axis, stance=stance, ref=ref, digest='synthetic-digest', origin='synthetic-run')


def test_configured_does_not_imply_other_dimensions_or_authority():
    result = readiness_report(context(), [record('configured')])
    assert result['conditions']['configured']['status'] == 'supported'
    assert all(result['conditions'][a]['status'] == 'unknown' for a in AXES if a != 'configured')
    assert result['execution_authorized'] is False and result['acceptance'] == 'pending'


@pytest.mark.parametrize('field', list(context()))
def test_other_context_evidence_never_establishes_readiness_or_leaks(field):
    observation = record(); observation['context'][field] = 'other-private-context'
    result = readiness_report(context(), [observation])
    assert result['conditions']['loaded'] == {'status': 'unknown', 'evidence': [], 'reason': 'no-applicable-record'}
    assert 'synthetic-ref' not in str(result) and 'other-private-context' not in str(result)


def test_conflict_preserves_both_stances_and_repeated_refs_do_not_vote():
    positive, adverse = record(), record(stance='contradicted', ref='adverse')
    result = readiness_report(context(), [positive, positive, adverse])
    loaded = result['conditions']['loaded']
    assert loaded['status'] == 'conflicting' and len(loaded['evidence']) == 2
    assert {e['stance'] for e in loaded['evidence']} == {'supported', 'contradicted'}


def test_policy_contradiction_is_separate_from_callability():
    result = readiness_report(context(), [record('callable'), record('policy', 'contradicted', 'revocation')])
    assert result['conditions']['callable']['status'] == 'supported'
    assert result['conditions']['policy']['status'] == 'contradicted'
    assert result['execution_authorized'] is False


def test_conflicting_reference_digest_refused():
    first, changed = record(), record(); changed['digest'] = 'changed'
    with pytest.raises(ValueError): readiness_report(context(), [first, changed])


def test_report_is_order_independent_and_does_not_modify_inputs():
    rows = [record('configured'), record('policy', 'contradicted', 'deny')]
    original = deepcopy(rows)
    assert readiness_report(context(), rows) == readiness_report(context(), list(reversed(rows)))
    assert rows == original


def test_positive_all_axes_still_does_not_authorize_execution():
    result = readiness_report(context(), [record(axis, ref=axis) for axis in AXES])
    assert all(c['status'] == 'supported' for c in result['conditions'].values())
    assert result['execution_authorized'] is False and result['acceptance'] == 'pending'
