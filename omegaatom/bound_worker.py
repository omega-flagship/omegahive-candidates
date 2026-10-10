"""Maintenance consumer of existing assigned bound requests; no scheduling/I/O.

This adapter targets the current HTTP Scientist route, not the unfrozen S3 ABI.
"""
import copy
import datetime
import json
from .envelope import loads, validate, digest, require
from .planner import plan, validate_proposal


def active(goal, agent_id):
    require(goal.get("status") == "claimed" and goal.get("claimed_by") == agent_id, "worker has no active claim")
    require(goal.get("assignee") in (None, agent_id), "wrong maintenance assignee")
    now = datetime.datetime.now(datetime.timezone.utc)
    for field in ("deadline_at", "lease_until"):
        if goal.get(field):
            try:
                deadline = datetime.datetime.fromisoformat(goal[field].replace("Z", "+00:00"))
                require(deadline.tzinfo is not None and deadline > now, field + " expired")
            except (TypeError, ValueError) as error:
                from .envelope import Refused
                raise Refused(field + " invalid or expired") from error


def validate_result(result, snapshot):
    snapshot = validate(snapshot)
    require(isinstance(result, dict) and set(result) == {"schema", "base_revision", "base_digest", "proposals", "authority"}, "maintenance result fields mismatch")
    require(result["schema"] == "omegaatom/maintenance-result/1" and result["authority"] == "none", "maintenance result cannot grant authority")
    require(result["base_revision"] == snapshot["revision"] and result["base_digest"] == digest(snapshot), "maintenance result stale")
    require(isinstance(result["proposals"], list) and len(result["proposals"]) <= 2000, "maintenance result proposal bound")
    identities = set()
    for p in result["proposals"]:
        validated = validate_proposal(p, snapshot)
        require(validated["id"] not in identities, "duplicate maintenance proposal")
        identities.add(validated["id"])
    return copy.deepcopy(result)


def prepare(goal, exhibit, agent_id, *, now):
    # Reuse platform's existing binding and exhibit digest algorithms.
    from hive.core.goals import binding_digest, MAX_RESULT_DATA_BYTES
    from hive.core.shares import exhibit_digest
    active(goal, agent_id)
    binding = goal.get("binding", {})
    bound = binding_digest(binding)
    require(goal.get("binding_digest") == bound, "maintenance binding mismatch")
    require(exhibit.get("kind") == "exhibit" and exhibit.get("complete") is True and exhibit.get("offset") == 0, "maintenance exhibit incomplete")
    require(exhibit.get("share_id") in binding.get("share_ids", []), "unbound maintenance exhibit")
    actual = exhibit_digest(exhibit["title"], exhibit["body"], exhibit["atoms"])
    require(actual == exhibit.get("digest") == binding.get("snapshot_digest"), "maintenance exhibit digest mismatch")
    snapshot = loads(exhibit["body"])
    require(snapshot["revision"] == binding.get("base_revision") and digest(snapshot) == binding.get("envelope_digest"), "maintenance snapshot binding mismatch")
    result = validate_result({"schema": "omegaatom/maintenance-result/1", "base_revision": snapshot["revision"],
                              "base_digest": digest(snapshot), "proposals": plan(snapshot, now), "authority": "none"}, snapshot)
    data = {"binding_digest": bound, "proposal": result}
    require(len(json.dumps(data).encode()) <= MAX_RESULT_DATA_BYTES, "maintenance result exceeds host byte bound")
    return {"goal_id": goal["id"], "agent_id": agent_id, "binding_digest": bound, "proposal": result,
            "data": data, "result": "Bound maintenance proposals; owner review pending."}


def finalize(prepared, fresh_goal, current_snapshot):
    from hive.core.goals import binding_digest
    active(fresh_goal, prepared["agent_id"])
    require(fresh_goal["id"] == prepared["goal_id"], "maintenance goal changed")
    require(binding_digest(fresh_goal["binding"]) == fresh_goal.get("binding_digest") == prepared["binding_digest"], "maintenance binding changed")
    validate_result(prepared["proposal"], current_snapshot)
    return {"status": "done", "result": prepared["result"], "data": copy.deepcopy(prepared["data"])}
