"""Pure domain proposals; not Learn's wire schema, authentication or writeback.

A trusted host adapter must resolve decisions and reviewer receipts. No adapter
is installed here. Export requires Learn's separately owned encoder/validator.
"""
from __future__ import annotations

import copy
from datetime import datetime
import hashlib
import json


def digest(value):
    return "sha256:" + hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()).hexdigest()


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _binding(value):
    if not isinstance(value, dict) or set(value) != {"id", "revision", "digest"}:
        raise ValueError("exact source binding required")
    d = value["digest"]
    if (not _text(value["id"]) or not _text(value["revision"])
            or not isinstance(d, str) or not d.startswith("sha256:")
            or len(d) != 71 or any(c not in "0123456789abcdef" for c in d[7:])):
        raise ValueError("invalid source binding")


def _time(value):
    if not isinstance(value, str):
        raise ValueError("timestamp required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone required")
    return parsed


def _decision(binding, resolve):
    _binding(binding)
    value = copy.deepcopy(resolve(copy.deepcopy(binding)))
    if not isinstance(value, dict) or value.get("binding") != binding:
        raise ValueError("missing or stale host decision")
    if value.get("answer") not in {"once", "for", "always", "no", "never"}:
        raise ValueError("unsupported five-answer decision")
    if not _text(value.get("person_id")) or value.get("authenticated") is not True:
        raise ValueError("named authenticated person required")
    scope = value.get("scope")
    if (not isinstance(scope, dict) or set(scope) != {"subject_id", "skill", "purpose"}
            or not all(_text(v) for v in scope.values())):
        raise ValueError("exact subject, skill and purpose required")
    if not _text(value.get("stamp")):
        raise ValueError("source stamp required")
    _time(value.get("at"))
    return value


def propose_correction(assessment, earlier, later, *, resolve_decision, dissent=()):
    """Produce advisory content from host-resolved decision metadata only.

    A later No is scoped to that decision, not a standing ban. Even Never is
    only recorded as a standing-policy review request: this function cannot
    supersede a policy or claim the underlying tie bug occurred.
    """
    _binding(assessment)
    before = _decision(earlier, resolve_decision)
    after = _decision(later, resolve_decision)
    if before["scope"] != after["scope"] or before["person_id"] != after["person_id"]:
        raise ValueError("scope or decision-maker mismatch")
    if earlier["id"] == later["id"] or before["stamp"] == after["stamp"]:
        raise ValueError("repeated evidence is not a new decision")
    if _time(after["at"]) <= _time(before["at"]):
        raise ValueError("strictly later decision required")
    if before["answer"] not in {"once", "for", "always"} or after["answer"] not in {"no", "never"}:
        raise ValueError("positive-to-negative correction required")
    if not isinstance(dissent, (tuple, list)) or not all(_text(v) for v in dissent):
        raise ValueError("dissent must be verbatim text")
    revision = {
        "kind": "governance-interpretation-correction",
        "scope": copy.deepcopy(after["scope"]),
        "person_id": after["person_id"],
        "lesson": "An earlier approval pattern does not authorize a later declined decision.",
        "later_answer": after["answer"],
        "policy_followup": "review-standing-rule" if after["answer"] == "never" else "respect-this-decline",
        "authority": "none",
        "confidence": None,
        "dissent": list(dissent),
    }
    content = {
        "assessment": copy.deepcopy(assessment),
        "earlier_decision": before,
        "consequence_or_appeal": after,
        "proposed_revision": revision,
        "proposed_revision_digest": digest(revision),
        "limits": ["No policy execution observed", "No ethical Ground change", "No memory write"],
    }
    return {"content": content, "digest": digest(content), "review": "pending", "authority": "none"}


def reviewed_correction(proposal, reviewer_receipt, *, resolve_review, producer_id):
    """Bind an independent assurance review to this exact proposal."""
    value = copy.deepcopy(proposal)
    if value.get("review") != "pending" or value.get("authority") != "none":
        raise ValueError("pending advisory proposal required")
    content = value.get("content")
    if not isinstance(content, dict) or value.get("digest") != digest(content):
        raise ValueError("proposal changed")
    if content.get("proposed_revision_digest") != digest(content.get("proposed_revision")):
        raise ValueError("revision changed")
    _binding(reviewer_receipt)
    receipt = copy.deepcopy(resolve_review(copy.deepcopy(reviewer_receipt)))
    expected = {
        "assessment": content["assessment"],
        "consequence_or_appeal": content["consequence_or_appeal"]["binding"],
        "proposal_digest": value["digest"],
        "proposed_revision_digest": content["proposed_revision_digest"],
    }
    if (not isinstance(receipt, dict) or receipt.get("binding") != reviewer_receipt
            or receipt.get("targets") != expected or receipt.get("authenticated") is not True
            or receipt.get("role") != "assurance" or receipt.get("verdict") != "accepted"
            or not _text(producer_id) or not _text(receipt.get("reviewer_id"))
            or receipt["reviewer_id"] == producer_id):
        raise ValueError("independent exact assurance review required")
    value["review"] = "accepted-proposal-only"
    value["reviewer_receipt"] = receipt
    value["producer_id"] = producer_id
    return value


def export_to_learn(proposal, *, encode, validate, resolve_decision=None, resolve_review=None):
    """Re-resolve current evidence/review, then use Learn-owned admission.

    Resolvers must refuse withdrawn or no-longer-visible records. This is a
    read-only preflight, not atomic host admission: the receiving host must
    recheck custody, currentness and grants in its own admission transaction.
    """
    if proposal.get("review") != "accepted-proposal-only":
        raise ValueError("review required before Learn export")
    pending = copy.deepcopy(proposal)
    receipt = pending.pop("reviewer_receipt")
    producer = pending.pop("producer_id")
    pending["review"] = "pending"
    reviewed_correction(pending, receipt["binding"], resolve_review=lambda _: receipt,
                        producer_id=producer)
    if encode is None or validate is None:
        raise ValueError("Learn schema adapter unavailable")
    if resolve_decision is None or resolve_review is None:
        raise ValueError("current trusted resolvers required")
    c = pending["content"]
    refreshed = propose_correction(c["assessment"], c["earlier_decision"]["binding"],
        c["consequence_or_appeal"]["binding"], resolve_decision=resolve_decision,
        dissent=c["proposed_revision"]["dissent"])
    if refreshed != pending:
        raise ValueError("source changed; independent review must be renewed")
    current = reviewed_correction(refreshed, receipt["binding"],
                                 resolve_review=resolve_review, producer_id=producer)
    if current != proposal:
        raise ValueError("review changed; independent review must be renewed")
    event = encode(copy.deepcopy(proposal))
    if validate(copy.deepcopy(event)) is not True:
        raise ValueError("Learn envelope refused")
    return copy.deepcopy(event)


def learning_event(proposal, *, event_id, owner, scope, subject, evidence_refs,
                   permissions, corrections=()):
    """Encode Learn's published event/1 fields, not a second schema.

    Subject is the exact owner export tuple, not a hash of this normalized
    projection. Evidence IDs must be resolved through OmegaAtom by Learn's
    trusted admission validator. Calling this encoder confers no visibility.
    """
    _binding(subject)
    if not all(_text(v) for v in (event_id, owner, scope)):
        raise ValueError("event identity and owner scope required")
    if (not isinstance(evidence_refs, (list, tuple)) or not evidence_refs
            or not all(_text(v) for v in evidence_refs)
            or len(set(evidence_refs)) != len(evidence_refs)):
        raise ValueError("unique eligible OmegaAtom evidence references required")
    if (not isinstance(permissions, dict) or set(permissions) != {"audiences", "derive", "redistribute"}
            or type(permissions["derive"]) is not bool or type(permissions["redistribute"]) is not bool
            or not isinstance(permissions["audiences"], list)
            or not all(_text(v) for v in permissions["audiences"])):
        raise ValueError("explicit permission declarations required")
    if not isinstance(corrections, (tuple, list)) or not all(_text(v) for v in corrections):
        raise ValueError("prior LearningEvent IDs required")
    c = proposal["content"]
    wire_subject = copy.deepcopy(subject)
    # Learn core.subject uses bare SHA-256; local bindings retain the prefix.
    wire_subject["digest"] = wire_subject["digest"][7:]
    return {
        "schema": "omegalearn/event/1", "id": event_id, "owner": owner, "scope": scope,
        "subject": wire_subject, "evidence_refs": list(evidence_refs),
        "predictions": [], "assumptions": [c["earlier_decision"]["binding"]["id"]],
        "review_findings": [proposal["reviewer_receipt"]["binding"]["id"]],
        "outcome_refs": [c["consequence_or_appeal"]["binding"]["id"]],
        "corrections": list(corrections), "permissions": copy.deepcopy(permissions),
        "payload": {"kind": "correction", "data": copy.deepcopy(proposal)},
    }
