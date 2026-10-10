"""Pure proposal admission candidate, not appraisal or authentication.

ReviewContext and AdoptionView must come from a trusted host bridge. No bridge
exists yet: tests use explicit synthetic doubles. Model input cannot supply
either object. This module neither adopts values nor executes findings.
"""
import copy
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from typing import Callable


@dataclass(frozen=True)
class ReviewContext:
    request_id: str
    subject: dict
    reviewer_id: str
    mandate: dict
    observed_from: str
    observed_to: str
    evidence_refs: tuple[str, ...]
    adoption_id: str | None
    subject_visible: bool
    active: bool


@dataclass(frozen=True)
class AdoptionView:
    adoption_id: str
    baseline: dict
    subject_id: str
    effective_from: str
    effective_to: str | None
    adopted_by: str
    authority_source: str
    supersedes: str | None = None


def _text(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 4000


def _time(value):
    if not isinstance(value, str):
        raise ValueError("invalid timestamp")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid timestamp") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("timestamp needs a timezone")
    return result


def _binding(value):
    if not isinstance(value, dict) or set(value) != {"artifact_id", "revision", "digest"}:
        raise ValueError("invalid artifact binding")
    digest = value["digest"]
    if (not _text(value["artifact_id"]) or type(value["revision"]) is not int
            or value["revision"] < 1 or not isinstance(digest, str)
            or len(digest) != 71 or not digest.startswith("sha256:")
            or any(c not in "0123456789abcdef" for c in digest[7:])):
        raise ValueError("invalid artifact identity")


def admit_proposal(context: ReviewContext, proposal: dict, *,
                   resolve_adoption: Callable[[str], AdoptionView | None] | None = None):
    """Return a detached advisory receipt after normalized host binding checks.

    A receipt means proposal admission, never truth, moral validity or effect
    authority. Resolver identity, authenticity and scope are host obligations.
    """
    if not isinstance(context, ReviewContext) or context.active is not True:
        raise ValueError("live host context required")
    if context.subject_visible is not True:
        raise ValueError("subject must be able to see and answer its finding")
    _binding(context.subject)
    if not _text(context.request_id) or not _text(context.reviewer_id):
        raise ValueError("missing host identity")
    if context.mandate not in ({"id": "alignment-drift", "version": "1"},
                               {"id": "alignment-flourishing", "version": "1"}):
        raise ValueError("unsupported specialist mandate")
    start, end = _time(context.observed_from), _time(context.observed_to)
    if start >= end:
        raise ValueError("invalid observed interval")
    if (not isinstance(context.evidence_refs, tuple)
            or not all(_text(ref) for ref in context.evidence_refs)
            or len(context.evidence_refs) != len(set(context.evidence_refs))):
        raise ValueError("invalid granted evidence references")
    fields = {"request_id", "subject", "mandate", "interval", "adoption_id", "baseline",
              "findings", "gaps", "rationale", "authority"}
    if not isinstance(proposal, dict) or set(proposal) != fields:
        raise ValueError("invalid proposal shape; global alignment and execution claims are unsupported")
    try:
        payload = json.dumps(proposal, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("proposal must be finite JSON data") from exc
    if len(payload.encode()) > 64_000:
        raise ValueError("proposal exceeds admission bound")
    if (proposal["request_id"] != context.request_id or proposal["subject"] != context.subject
            or proposal["mandate"] != context.mandate or proposal["interval"] !=
            {"from": context.observed_from, "to": context.observed_to}
            or proposal["adoption_id"] != context.adoption_id):
        raise ValueError("proposal binding mismatch")
    if proposal["authority"] != "none" or not _text(proposal["rationale"]):
        raise ValueError("advisory rationale required")
    gaps = proposal["gaps"]
    if (not isinstance(gaps, list) or len(gaps) > 100 or not all(_text(x) for x in gaps)
            or len(gaps) != len(set(gaps))):
        raise ValueError("invalid gap list")
    adopted = None
    if context.adoption_id is None:
        if proposal["baseline"] is not None or "missing-adopted-baseline" not in gaps:
            raise ValueError("missing baseline must remain an explicit gap")
    else:
        if not _text(context.adoption_id) or resolve_adoption is None:
            raise ValueError("trusted adoption resolver required")
        adopted = resolve_adoption(context.adoption_id)
        if (not isinstance(adopted, AdoptionView) or adopted.adoption_id != context.adoption_id
                or adopted.subject_id != context.subject["artifact_id"]
                or not _text(adopted.adopted_by) or not _text(adopted.authority_source)):
            raise ValueError("adoption unavailable or outside subject scope")
        _binding(adopted.baseline)
        if proposal["baseline"] != adopted.baseline:
            raise ValueError("baseline revision mismatch")
        if (_time(adopted.effective_from) > start or adopted.effective_to is not None
                and end > _time(adopted.effective_to)):
            raise ValueError("adoption does not cover the whole observed interval")
    findings = proposal["findings"]
    if not isinstance(findings, list) or len(findings) > 100:
        raise ValueError("invalid findings")
    ids = set()
    for f in findings:
        if not isinstance(f, dict) or set(f) != {"id", "change", "evidence", "legitimacy", "evidence_refs", "claim"}:
            raise ValueError("invalid finding shape")
        if not _text(f["id"]) or f["id"] in ids or not _text(f["claim"]):
            raise ValueError("invalid finding identity")
        ids.add(f["id"])
        if (not isinstance(f["change"], str) or f["change"] not in {"unchanged", "changed", "unknown"}
                or not isinstance(f["evidence"], str) or f["evidence"] not in {"supported", "contradicted", "mixed", "unknown"}
                or not isinstance(f["legitimacy"], str) or f["legitimacy"] not in
                {"within-baseline", "authorized-amendment", "unresolved-authority", "violation"}):
            raise ValueError("invalid separate finding judgments")
        refs = f["evidence_refs"]
        if (not isinstance(refs, list) or not all(_text(ref) for ref in refs)
                or len(refs) != len(set(refs)) or not set(refs).issubset(context.evidence_refs)):
            raise ValueError("finding cites evidence outside the request")
        if f["evidence"] in {"supported", "contradicted", "mixed"} and not refs:
            raise ValueError("evidence-backed claim needs references")
        if adopted is None and f["legitimacy"] != "unresolved-authority":
            raise ValueError("no baseline for this legitimacy claim")
        if f["legitimacy"] == "authorized-amendment" and not adopted.supersedes:
            raise ValueError("amendment needs host supersession")
    return {"request_id": context.request_id, "reviewer_id": context.reviewer_id,
            "proposal_digest": "sha256:" + hashlib.sha256(payload.encode()).hexdigest(),
            "proposal": copy.deepcopy(proposal), "authority": "none",
            "claim_ceiling": "proposal-admission-only"}
