"""Offline maintenance proposals, never execution or authority."""
import copy
import math
from .envelope import validate, digest, evidence_id, lineage_state, require


def plan(snapshot, now):
    snapshot = validate(snapshot)
    require(type(now) in (int, float) and math.isfinite(now) and now >= 0, "invalid planner time")
    base = digest(snapshot)
    records = {evidence_id(r["id"]): r for r in snapshot["records"]}
    state = {evidence_id(s["id"]): s for s in lineage_state(snapshot)}
    proposals = []
    def emit(action, targets, dependencies, expected, unresolved):
        payload = {"version": "0.1", "owner": snapshot["owner"], "scope": snapshot["scope"],
                   "base_revision": snapshot["revision"], "base_digest": base,
                   "action": action, "targets": [list(t) for t in sorted(targets)],
                   "evidence_dependencies": [list(t) for t in sorted(dependencies)],
                   "retention": [{"id": list(t), **records[t].get("retention", {})} for t in sorted(targets)],
                   "expected_effect": expected, "unresolved": unresolved, "authority": "none"}
        proposals.append({"id": digest(payload), **payload})
    for key, s in state.items():
        if s["stale"]:
            emit("mark-stale", [key], [evidence_id(e) for e in s["causes"]],
                 "Exclude this derivation from active conclusions; retain evidence and request re-derivation.", ["owner-admission", "host-write-seam"])
    for key, r in records.items():
        retention = r.get("retention", {})
        if retention.get("expires_at", math.inf) <= now:
            descendants = set()
            changed = True
            while changed:
                changed = False
                for child, cr in records.items():
                    if child != key and child not in descendants and any(evidence_id(p) in descendants | {key} for p in cr.get("premises", [])):
                        descendants.add(child)
                        changed = True
            live = sorted(d for d in descendants if not state[d]["retracted"] and not state[d]["stale"])
            blocked = retention.get("protected", False) or bool(live) or r["statement"][0] == "Retracted"
            emit("retain" if blocked else "archive-candidate", [key], live,
                 "Preserve protected/dependency/control evidence." if blocked else "Retire from active memory into owner-controlled archive; do not delete.",
                 ["retention-block"] if blocked else ["owner-admission", "archive-custody", "host-write-seam"])
    return copy.deepcopy(proposals)


def validate_proposal(proposal, snapshot):
    """Check binding/integrity only. Does not approve a proposal."""
    snapshot = validate(snapshot)
    require(isinstance(proposal, dict) and "id" in proposal, "invalid proposal")
    require(proposal["id"] == digest({k: v for k, v in proposal.items() if k != "id"}), "proposal digest mismatch")
    require(proposal.get("authority") == "none", "proposal cannot grant authority")
    require(proposal.get("owner") == snapshot["owner"] and proposal.get("scope") == snapshot["scope"], "owner/scope mismatch")
    require(proposal.get("base_revision") == snapshot["revision"] and proposal.get("base_digest") == digest(snapshot), "stale snapshot binding")
    require(proposal.get("action") in {"mark-stale", "retain", "archive-candidate"}, "unsupported action")
    index = {evidence_id(r["id"]) for r in snapshot["records"]}
    for field in ("targets", "evidence_dependencies"):
        require(isinstance(proposal.get(field), list), "missing targets/dependencies")
        for value in proposal[field]:
            require(evidence_id(value) in index, "unknown proposal target/dependency")
    require(bool(proposal["targets"]), "empty targets")
    return copy.deepcopy(proposal)
