import copy
from dataclasses import replace
import pytest
from omegaalignment.assessment import AdoptionView, ReviewContext, admit_proposal


def case():
    subject = {"artifact_id": "synthetic-behavior", "revision": 1, "digest": "sha256:" + "a" * 64}
    baseline = {"artifact_id": "synthetic-baseline", "revision": 1, "digest": "sha256:" + "b" * 64}
    context = ReviewContext("synthetic-request", subject, "synthetic-reviewer",
                            {"id": "alignment-drift", "version": "1"},
                            "2026-10-04T00:10:00Z", "2026-10-04T00:20:00Z",
                            ("synthetic-witness",), "synthetic-adoption", True, True)
    adoption = AdoptionView("synthetic-adoption", baseline, "synthetic-behavior",
                            "2026-10-04T00:00:00Z", "2026-10-04T01:00:00Z",
                            "synthetic-person", "synthetic-host-double")
    proposal = {"request_id": context.request_id, "subject": subject, "mandate": context.mandate,
                "interval": {"from": context.observed_from, "to": context.observed_to},
                "adoption_id": context.adoption_id, "baseline": baseline,
                "findings": [{"id": "synthetic-finding", "change": "changed", "evidence": "supported",
                              "legitimacy": "within-baseline", "evidence_refs": ["synthetic-witness"],
                              "claim": "New evidence changed a prediction; commitment unchanged."}],
                "gaps": ["real-outcome-not-observed"], "rationale": "Synthetic proposal only.", "authority": "none"}
    return context, adoption, proposal


def test_supported_learning_retains_change_evidence_legitimacy_and_gap():
    context, adoption, proposal = case()
    receipt = admit_proposal(context, proposal, resolve_adoption=lambda _: adoption)
    assert receipt["proposal"] == proposal and receipt["authority"] == "none"
    proposal["gaps"].clear()
    assert receipt["proposal"]["gaps"] == ["real-outcome-not-observed"]
    assert receipt["claim_ceiling"] == "proposal-admission-only"


def test_no_baseline_is_only_admitted_as_explicit_unresolved_gap():
    context, _, p = case()
    context = replace(context, adoption_id=None)
    p.update(adoption_id=None, baseline=None, gaps=["missing-adopted-baseline"])
    p["findings"][0]["legitimacy"] = "unresolved-authority"
    assert admit_proposal(context, p)["proposal"]["gaps"]
    p["findings"][0]["legitimacy"] = "within-baseline"
    with pytest.raises(ValueError): admit_proposal(context, p)


@pytest.mark.parametrize("mutation", ["subject", "revision", "request", "interval", "baseline", "evidence",
                                    "execute", "aligned", "authority", "duplicate", "empty-evidence", "amendment"])
def test_model_changes_cannot_escape_binding_or_invent_authority(mutation):
    c, a, p = copy.deepcopy(case())
    if mutation == "subject": p["subject"]["artifact_id"] = "another-subject"; c = replace(c, subject=case()[0].subject)
    if mutation == "revision": p["subject"]["revision"] = 2; c = replace(c, subject=case()[0].subject)
    if mutation == "request": p["request_id"] = "another-request"
    if mutation == "interval": p["interval"]["to"] = "2026-10-04T00:30:00Z"
    if mutation == "baseline": p["baseline"] = {**p["baseline"], "revision": 2}
    if mutation == "evidence": p["findings"][0]["evidence_refs"] = ["ungranted-source"]
    if mutation in {"execute", "aligned"}: p[mutation] = True
    if mutation == "authority": p["authority"] = "hold"
    if mutation == "duplicate": p["findings"].append(copy.deepcopy(p["findings"][0]))
    if mutation == "empty-evidence": p["findings"][0]["evidence_refs"] = []
    if mutation == "amendment": p["findings"][0]["legitimacy"] = "authorized-amendment"
    with pytest.raises(ValueError): admit_proposal(c, p, resolve_adoption=lambda _: a)


@pytest.mark.parametrize("mutation", ["ended", "invisible", "no-resolver", "foreign-adoption", "future-adoption", "expired-adoption", "no-person"])
def test_trusted_context_must_establish_live_scope_and_applicable_adoption(mutation):
    c, a, p = case()
    resolver = lambda _: a
    if mutation == "ended": c = replace(c, active=False)
    if mutation == "invisible": c = replace(c, subject_visible=False)
    if mutation == "no-resolver": resolver = None
    if mutation == "foreign-adoption": a = replace(a, subject_id="foreign-subject")
    if mutation == "future-adoption": a = replace(a, effective_from="2026-10-04T00:11:00Z")
    if mutation == "expired-adoption": a = replace(a, effective_to="2026-10-04T00:19:00Z")
    if mutation == "no-person": a = replace(a, adopted_by="")
    with pytest.raises(ValueError): admit_proposal(c, p, resolve_adoption=resolver)


def test_authorized_amendment_requires_supersession_and_preserves_unknowns():
    c, a, p = case()
    a = replace(a, supersedes="prior-synthetic-adoption")
    p["findings"][0].update(legitimacy="authorized-amendment", evidence="unknown", evidence_refs=[])
    out = admit_proposal(c, p, resolve_adoption=lambda _: a)
    assert out["proposal"]["findings"][0]["evidence"] == "unknown"


def test_missing_baseline_gap_cannot_be_omitted():
    c, _, p = case()
    c = replace(c, adoption_id=None)
    p.update(adoption_id=None, baseline=None, gaps=[])
    with pytest.raises(ValueError): admit_proposal(c, p)
