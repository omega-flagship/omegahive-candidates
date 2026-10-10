"""L0 interoperability with Learn's actual library; synthetic custody only."""
import copy
import pytest
from omegalearn.core import Ledger, Refused, event_shape
from omegaalignment.learning import export_to_learn, learning_event
from omegaalignment.tests.test_learning import binding, case, reviewed


def event():
    records, propose = case()
    p = reviewed(propose())
    def encode(value):
        return learning_event(value, event_id="alignment/correction-1", owner="alignment", scope="bounded-case",
            subject=binding("owner-export"), evidence_refs=["atom/decision-1", "atom/decision-2"],
            permissions={"audiences": ["learn"], "derive": True, "redistribute": False})
    def validate(value):
        event_shape(value)
        return True
    return export_to_learn(p, encode=encode, validate=validate,
        resolve_decision=lambda ref: records[ref["id"]], resolve_review=lambda _: p["reviewer_receipt"])


def trusted(value):
    # Explicit synthetic resolver, not proof of host authentication or grants.
    refs = sum([value[k] for k in ("evidence_refs", "predictions", "assumptions", "review_findings", "outcome_refs")], [])
    return {"current_subject": value["subject"], "owner": value["owner"], "scope": value["scope"],
            "permissions": value["permissions"], "visible_refs": refs, "references_valid": True}


def test_alignment_event_admitted_by_actual_learn_library_once():
    e = event()
    ledger = Ledger()
    assert ledger.admit(e, trusted)["new_evidence"] is True
    assert ledger.admit(copy.deepcopy(e), trusted)["new_evidence"] is False
    assert len(e["subject"]["digest"]) == 64
    assert e["payload"]["data"]["authority"] == "none"


@pytest.mark.parametrize("override", [{"current_subject": None}, {"permissions": {}}, {"visible_refs": []}])
def test_actual_learn_refuses_stale_ungranted_or_unresolved_export(override):
    with pytest.raises(Refused):
        Ledger().admit(event(), lambda e: {**trusted(e), **override})
