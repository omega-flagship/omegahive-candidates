"""Read-only governance eligibility using the accepted OmegaAtom library.

Does not authenticate custody, create evidence or define reference encoding.
The host supplies a granted projection and exact required Source tuples.
"""
import copy
from omegaatom.envelope import (validate, lineage_state, evidence_id, revision_allowed,
                                format_evidence_ref, parse_evidence_ref)
from .learning import learning_event


def governance_sources(snapshot, required):
    """Return known observed, independent and unwithdrawn exact sources.

    required is a list of {id: structured Atom ID, source: exact Source tuple}.
    This local input is not a new cross-module evidence envelope. No statement
    is interpreted as an authenticated person's decision by this function.
    """
    projection = validate(copy.deepcopy(snapshot))
    if not isinstance(required, list) or len(required) < 2:
        raise ValueError("at least two bound governance sources required")
    index = {evidence_id(r["id"]): r for r in projection["records"]}
    state = {evidence_id(r["id"]): r for r in lineage_state(projection)}
    selected, seen = [], set()
    for item in required:
        if not isinstance(item, dict) or set(item) != {"id", "source"}:
            raise ValueError("exact evidence ID and Source required")
        key = evidence_id(item["id"])
        if key in seen or key not in index:
            raise ValueError("duplicate or missing evidence")
        seen.add(key)
        r = index[key]
        if r["source"] != item["source"]:
            raise ValueError("source binding mismatch")
        if state[key]["retracted"] or state[key]["stale"]:
            raise ValueError("withdrawn or stale governance evidence")
        if r["status"] != "observed" or r["unknown"]:
            raise ValueError("known observed governance evidence required")
        if r["statement"][0] == "Retracted":
            raise ValueError("retraction is not a person's approval decision")
        if any(not revision_allowed(r["stamp"], p["stamp"]) for p in selected):
            raise ValueError("overlapping evidence stamps")
        selected.append(r)
    return copy.deepcopy(selected)


def learn_references(records, *, format_reference=format_evidence_ref, parse_reference=parse_evidence_ref):
    """Consume Atom-owned lossless reference functions, never define a codec."""
    if format_reference is None or parse_reference is None:
        raise ValueError("OmegaAtom canonical reference API required")
    refs = []
    for r in records:
        key = evidence_id(r["id"])
        ref = format_reference(copy.deepcopy(r["id"]))
        if not isinstance(ref, str) or evidence_id(list(parse_reference(ref))) != key:
            raise ValueError("reference codec must preserve exact evidence identity")
        if ref in refs:
            raise ValueError("reference collision")
        refs.append(ref)
    return refs


def governance_learning_event(proposal, *, snapshot, required, event_id, owner,
                              subject, permissions, corrections=()):
    """Encode a reviewed correction using its exact eligible Atom sources.

    Source tuples must bind the two host decision records in order. Snapshot
    permission and the export subject's custody still require Learn's trusted
    admission resolver. This function neither authenticates decisions nor
    assigns host evidence IDs.
    """
    if proposal.get("review") != "accepted-proposal-only":
        raise ValueError("reviewed proposal required")
    records = governance_sources(snapshot, required)
    c = proposal["content"]
    bindings = [c["earlier_decision"]["binding"], c["consequence_or_appeal"]["binding"]]
    if len(records) != len(bindings):
        raise ValueError("exactly the two decision sources required")
    for record, binding in zip(records, bindings):
        source = record["source"]
        if (source["subject"] != binding["id"] or str(source["revision"]) != binding["revision"]
                or source["digest"] != binding["digest"][7:]):
            raise ValueError("Atom source does not bind proposal decision")
    return learning_event(proposal, event_id=event_id, owner=owner, scope=snapshot["scope"],
        subject=subject, evidence_refs=learn_references(records),
        permissions=permissions, corrections=corrections)
