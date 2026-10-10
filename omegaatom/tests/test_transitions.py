import copy
import json
import pytest
from omegaatom import Refused, validate, lineage_state, stage_append, lineage_delta, dumps, loads
from omegaatom.envelope import digest
from test_envelope import chain, record, retract, snapshot, ev


def append(s, records):
    return stage_append(s, records, expected_revision=s["revision"], expected_digest=digest(s))


def test_withdraw_restore_delta_and_no_input_mutation():
    s = chain()
    before = copy.deepcopy(s)
    staged = append(s, [retract(5, 1)])
    assert s == before
    delta = staged["delta"]
    assert delta["newly_stale"] == [ev(2), ev(3)]
    assert delta["newly_retracted"] == [ev(1)]
    assert delta["newly_eligible"] == []
    restored = append(staged["snapshot"], [retract(6, 5)])
    assert restored["delta"]["newly_eligible"] == [ev(1), ev(2), ev(3)]
    assert restored["delta"]["newly_retracted"] == [ev(5)]
    assert restored["delta"]["authority"] == "none"
    assert lineage_state(loads(dumps(restored["snapshot"]))) == lineage_state(restored["snapshot"])


def test_independent_retraction_prevents_false_restoration():
    a = append(chain(), [retract(5, 1), retract(6, 1)])
    b = append(a["snapshot"], [retract(7, 5)])
    assert b["delta"]["newly_eligible"] == []


def test_append_binding_batch_failure_and_source_preservation():
    s = chain()
    for expected_revision, expected_digest in [(True, digest(s)), (0, digest(s)), (s["revision"], "0" * 64)]:
        with pytest.raises(Refused, match="stale"):
            stage_append(s, [retract(5, 1)], expected_revision=expected_revision, expected_digest=expected_digest)
    before = copy.deepcopy(s)
    with pytest.raises(Refused, match="target"):
        append(s, [record(5), retract(6, 999)])
    assert before == s
    with pytest.raises(Refused, match="duplicate"):
        append(s, [record(1)])


def test_new_derivation_over_withdrawn_source_refused():
    s = append(chain(), [retract(5, 1)])["snapshot"]
    derived = record(6, "inferred", premises=[2])
    derived["stamp"] = [ev(1)]
    with pytest.raises(Refused, match="withdrawn"):
        append(s, [derived])


def test_same_batch_withdrawal_cannot_admit_new_derived_atom():
    derived = record(6, "inferred", premises=[1])
    derived["stamp"] = [ev(1)]
    with pytest.raises(Refused, match="withdrawn"):
        append(chain(), [derived, retract(5, 1)])


def test_valid_same_batch_derivation_and_no_premature_eligibility_claim():
    derived = record(6, "inferred", premises=[5])
    derived["stamp"] = [ev(5)]
    result = append(chain(), [derived, record(5)])
    assert result["delta"]["newly_stale"] == []
    assert result["delta"]["newly_eligible"] == []


@pytest.mark.parametrize("mutation", ["delete", "change", "scope", "revision"])
def test_delta_refuses_history_rewrite(mutation):
    s = chain()
    after = copy.deepcopy(s)
    after["revision"] += 1
    if mutation == "delete":
        after["records"].pop()
    elif mutation == "change":
        after["records"][-1]["truth"][1] = 0.7
    elif mutation == "scope":
        after["owner"] = "foreign"
    else:
        after["revision"] += 1
    with pytest.raises(Refused):
        lineage_delta(s, after)


@pytest.mark.parametrize("reverse", [False, True])
def test_actual_longest_depth_is_order_independent(reverse):
    records = [record(1)]
    for n in range(2, 130):
        r = record(n, "inferred", premises=[n-1])
        r["stamp"] = [ev(1)]
        records.append(r)
    if reverse:
        records.reverse()
    with pytest.raises(Refused, match="depth"):
        validate(snapshot(records))


def test_maximum_allowed_depth_remains_iterative():
    records = [record(1)]
    for n in range(2, 129):
        r = record(n, "inferred", premises=[n-1])
        r["stamp"] = [ev(1)]
        records.append(r)
    assert len(lineage_state(snapshot(records))) == 128
