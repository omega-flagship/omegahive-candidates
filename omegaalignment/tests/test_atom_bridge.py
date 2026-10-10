import copy
import pytest
from omegaalignment.atom_bridge import governance_sources, learn_references, governance_learning_event
from omegaalignment.learning import export_to_learn
from omegaalignment.tests.test_learning import case, reviewed, binding
from omegaalignment.tests.test_learning_interop import trusted
from omegalearn.core import Ledger, event_shape
from omegaatom.projection import project_pages


def source(n):
    return {"owner": "governance", "subject": "approval-" + str(n), "revision": 1, "digest": str(n) * 64}


def record(n):
    return {"id": ["ev", "governance", n], "source": source(n), "scope": "alignment-case",
        "status": "observed", "unknown": False, "truth": ["stv", float(n == 1), 0.5],
        "stamp": [["ev", "governance", n]], "statement": ["Decision", "approval-" + str(n)]}


def packet():
    return {"version": "0.1", "owner": "governance", "scope": "alignment-case", "revision": 1,
            "records": [record(1), record(2)]}


def required():
    return [{"id": ["ev", "governance", n], "source": source(n)} for n in (1, 2)]


def test_actual_atom_library_selects_bound_independent_sources():
    p = packet()
    result = governance_sources(p, required())
    assert len(result) == 2
    p["records"][0]["statement"] = ["Changed"]
    assert result[0]["statement"] == ["Decision", "approval-1"]
    with pytest.raises(ValueError, match="canonical reference API"):
        learn_references(result, format_reference=None, parse_reference=None)


def test_actual_atom_retraction_blocks_governance_selection():
    p = packet()
    retract = record(3)
    retract["statement"] = ["Retracted", ["ev", "governance", 2], "withdrawn", "owner", 10]
    p["records"].append(retract)
    with pytest.raises(ValueError, match="withdrawn"):
        governance_sources(p, required())


@pytest.mark.parametrize("change", ["unknown", "source", "duplicate"])
def test_unusable_source_refuses(change):
    p, wanted = packet(), required()
    if change == "unknown":
        p["records"][1]["unknown"] = True
        p["records"][1].pop("truth")
    elif change == "source":
        wanted[1]["source"]["digest"] = "a" * 64
    else:
        wanted[1] = copy.deepcopy(wanted[0])
    with pytest.raises(ValueError):
        governance_sources(p, wanted)


def test_owner_codec_handles_colon_owner_without_local_encoding():
    r = record(1)
    r["id"] = ["ev", "hive:governance", 12]
    assert learn_references([r]) == ["ev:hive:governance:12"]


def pipeline():
    decisions, propose = case()
    proposal = reviewed(propose())
    p = packet()
    for r in p["records"]:
        ref = decisions[r["source"]["subject"]]["binding"]
        r["source"]["digest"] = ref["digest"][7:]
    wanted = [{"id": r["id"], "source": r["source"]} for r in p["records"]]
    def encode(value):
        return governance_learning_event(value, snapshot=p, required=wanted,
            event_id="alignment/governance-correction", owner="alignment", subject=binding("owner-export"),
            permissions={"audiences": ["learn"], "derive": True, "redistribute": False})
    def validate(e):
        event_shape(e)
        return True
    def export():
        return export_to_learn(proposal, encode=encode, validate=validate,
            resolve_decision=lambda ref: decisions[ref["id"]], resolve_review=lambda _: proposal["reviewer_receipt"])
    return p, export


def test_actual_atom_to_alignment_to_learn_library_path():
    _, export = pipeline()
    e = export()
    assert e["evidence_refs"] == ["ev:governance:1", "ev:governance:2"]
    assert Ledger().admit(e, trusted)["new_evidence"] is True


def test_valid_but_unrelated_atom_source_cannot_support_proposal():
    p, export = pipeline()
    p["records"][1]["source"]["subject"] = "unrelated-approval"
    with pytest.raises(ValueError, match="does not bind"):
        export()


def test_atom_withdrawal_between_review_and_export_blocks_pipeline():
    p, export = pipeline()
    r = record(3)
    r["statement"] = ["Retracted", ["ev", "governance", 2], "withdrawn", "owner", 10]
    p["records"].append(r)
    with pytest.raises(ValueError, match="withdrawn"):
        export()


def test_query_closure_preserves_withdrawal_and_controls_on_controls():
    p = packet()
    retract = record(3)
    retract["statement"] = ["Retracted", ["ev", "governance", 2], "withdrawn", "owner", 10]
    restore = record(4)
    restore["statement"] = ["Retracted", ["ev", "governance", 3], "restore-evidence", "owner", 11]
    p["records"].extend([retract, restore])
    pages = project_pages(p, [r["id"] for r in required()])
    assert len(pages) == 1 and pages[0]["closure_complete"] is True
    assert {r["id"][2] for r in pages[0]["snapshot"]["records"]} == {1, 2, 3, 4}
    assert len(governance_sources(pages[0]["snapshot"], required())) == 2
    # Restored eligibility is not a grant or writeback; only data is returned.


def test_independent_withdrawal_remains_active_in_query_closure():
    p = packet()
    for n, target in [(3, 2), (4, 3), (5, 2)]:
        r = record(n)
        r["statement"] = ["Retracted", ["ev", "governance", target], "control", "owner", 10 + n]
        p["records"].append(r)
    page, = project_pages(p, [r["id"] for r in required()])
    assert {r["id"][2] for r in page["snapshot"]["records"]} == {1, 2, 3, 4, 5}
    with pytest.raises(ValueError, match="withdrawn"):
        governance_sources(page["snapshot"], required())
