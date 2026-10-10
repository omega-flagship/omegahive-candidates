import copy
import pytest
from omegaalignment.learning import digest, propose_correction, reviewed_correction, export_to_learn, learning_event


def binding(name):
    return {"id": name, "revision": "1", "digest": digest(name)}


def case(answer="never"):
    a, b = binding("approval-1"), binding("approval-2")
    records = {}
    for ref, choice, at in [(a, "always", "2026-10-04T10:00:00Z"), (b, answer, "2026-10-04T11:00:00Z")]:
        records[ref["id"]] = dict(binding=ref, answer=choice, at=at,
            person_id="person-1", authenticated=True, stamp=ref["id"],
            scope={"subject_id": "subject-1", "skill": "example", "purpose": "bounded-case"})
    def propose():
        return propose_correction(binding("assessment"), a, b,
            resolve_decision=lambda ref: records[ref["id"]], dissent=["Reviewer uncertainty retained."])
    return records, propose


def reviewed(proposal, **changes):
    c = proposal["content"]
    receipt = dict(binding=binding("review"), authenticated=True, role="assurance",
        verdict="accepted", reviewer_id="reviewer", targets={
        "assessment": c["assessment"], "consequence_or_appeal": c["consequence_or_appeal"]["binding"],
        "proposal_digest": proposal["digest"], "proposed_revision_digest": c["proposed_revision_digest"]})
    receipt.update(changes)
    return reviewed_correction(proposal, binding("review"), resolve_review=lambda _: receipt, producer_id="alignment")


def test_deterministic_proposal_preserves_dissent_and_no_authority():
    records, propose = case()
    p = propose()
    assert p == propose()
    assert p["content"]["proposed_revision"]["dissent"] == ["Reviewer uncertainty retained."]
    records["approval-2"]["scope"]["skill"] = "changed"
    assert p["content"]["proposed_revision"]["scope"]["skill"] == "example"
    assert p["authority"] == "none"


def test_no_is_not_a_standing_ban():
    _, propose = case("no")
    assert propose()["content"]["proposed_revision"]["policy_followup"] == "respect-this-decline"


@pytest.mark.parametrize("field,value", [
    ("authenticated", False), ("stamp", "approval-1"),
    ("at", "2026-10-04T09:00:00Z"), ("person_id", "another-person"),
    ("answer", "always"), ("scope", {"subject_id": "other", "skill": "example", "purpose": "bounded-case"}),
])
def test_refuses_unbound_or_inapplicable_decisions(field, value):
    records, propose = case()
    records["approval-2"][field] = value
    with pytest.raises(ValueError):
        propose()


def test_exact_review_preserved_but_not_acceptance_authority():
    _, propose = case()
    p = reviewed(propose())
    assert p["reviewer_receipt"]["role"] == "assurance"
    assert p["authority"] == "none"
    with pytest.raises(ValueError, match="adapter unavailable"):
        export_to_learn(p, encode=None, validate=None)


@pytest.mark.parametrize("changes", [{"reviewer_id": "alignment"}, {"targets": {}}, {"verdict": "rejected"}])
def test_independent_review_required(changes):
    _, propose = case()
    with pytest.raises(ValueError):
        reviewed(propose(), **changes)


def test_changed_proposal_refused():
    _, propose = case()
    p = copy.deepcopy(propose())
    p["content"]["proposed_revision"]["dissent"] = []
    with pytest.raises(ValueError, match="changed"):
        reviewed(p)


def test_tampering_after_review_refused_before_export():
    _, propose = case()
    p = reviewed(propose())
    p["content"]["proposed_revision"]["scope"]["skill"] = "other"
    with pytest.raises(ValueError, match="changed"):
        export_to_learn(p, encode=lambda _: {}, validate=lambda _: True)


def test_shared_envelope_export_requires_external_admission():
    records, propose = case()
    p = reviewed(propose())
    def encode(value):
        return learning_event(value, event_id="alignment:event-1", owner="alignment", scope="bounded-case",
            subject=binding("exact-export"), evidence_refs=["atom:decision-1", "atom:decision-2"],
            permissions={"audiences": ["learn"], "derive": True, "redistribute": False})
    resolvers = {"resolve_decision": lambda ref: records[ref["id"]],
                 "resolve_review": lambda _: p["reviewer_receipt"]}
    with pytest.raises(ValueError, match="refused"):
        export_to_learn(p, encode=encode, validate=lambda _: False, **resolvers)
    # Synthetic callback checks structure only; does not establish host custody.
    event = export_to_learn(p, encode=encode, validate=lambda e: e["schema"] == "omegalearn/event/1", **resolvers)
    assert event["subject"] == dict(binding("exact-export"), digest=binding("exact-export")["digest"][7:])
    assert event["payload"]["data"]["content"]["proposed_revision_digest"] == p["content"]["proposed_revision_digest"]


def test_export_cannot_use_stored_authentication_as_current_custody():
    _, propose = case()
    with pytest.raises(ValueError, match="current trusted"):
        export_to_learn(reviewed(propose()), encode=lambda _: {}, validate=lambda _: True)


@pytest.mark.parametrize("withdrawn", ["earlier", "later", "review"])
def test_withdrawn_or_revoked_source_blocks_export(withdrawn):
    records, propose = case()
    p = reviewed(propose())
    missing = {"earlier": "approval-1", "later": "approval-2"}.get(withdrawn)
    with pytest.raises(ValueError):
        export_to_learn(p, encode=lambda _: {}, validate=lambda _: True,
            resolve_decision=lambda ref: None if ref["id"] == missing else records[ref["id"]],
            resolve_review=lambda _: None if withdrawn == "review" else p["reviewer_receipt"])


def test_changed_source_requires_fresh_independent_review():
    records, propose = case()
    p = reviewed(propose())
    records["approval-2"]["answer"] = "no"
    with pytest.raises(ValueError, match="source changed"):
        export_to_learn(p, encode=lambda _: {}, validate=lambda _: True,
            resolve_decision=lambda ref: records[ref["id"]],
            resolve_review=lambda _: p["reviewer_receipt"])
