"""Pure staging for the host's future atomic append seam; grants stay outside."""
import copy
from .envelope import validate, digest, lineage_state, evidence_id, require


def lineage_delta(before, after):
    """Append-only history comparison. Eligibility means lineage only."""
    before, after = validate(before), validate(after)
    require(before["owner"] == after["owner"] and before["scope"] == after["scope"], "owner/scope transition mismatch")
    require(after["revision"] == before["revision"] + 1, "transition must advance one revision")
    old = {evidence_id(r["id"]): r for r in before["records"]}
    new = {evidence_id(r["id"]): r for r in after["records"]}
    require(set(old) <= set(new) and all(old[k] == new[k] for k in old), "history rewrite/removal refused")
    prior = {evidence_id(r["id"]): r for r in lineage_state(before)}
    current = {evidence_id(r["id"]): r for r in lineage_state(after)}
    def eligible(r):
        return not r["stale"] and not r["retracted"]
    return {"base_revision": before["revision"], "base_digest": digest(before),
            "result_revision": after["revision"], "result_digest": digest(after),
            "newly_stale": [list(k) for k in sorted(current) if current[k]["stale"] and not prior.get(k, {}).get("stale", False)],
            "newly_retracted": [list(k) for k in sorted(current) if current[k]["retracted"] and not prior.get(k, {}).get("retracted", False)],
            "newly_eligible": [list(k) for k in sorted(prior) if not eligible(prior[k]) and eligible(current[k])],
            "authority": "none"}


def stage_append(snapshot, records, *, expected_revision, expected_digest):
    """Validate a host-issued batch against its closure. No ID mint or commit."""
    before = validate(snapshot)
    require(type(expected_revision) is int and before["revision"] == expected_revision and digest(before) == expected_digest, "stale append binding")
    require(isinstance(records, list) and bool(records), "nonempty append batch required")
    after = copy.deepcopy(before)
    after["records"].extend(copy.deepcopy(records))
    after["revision"] += 1
    after = validate(after)
    states = {evidence_id(r["id"]): r for r in lineage_state(after)}
    # Preserve historical stale records but refuse admission of fresh derivations
    # over withdrawn inputs, including withdrawals in this same batch.
    for record in records:
        if record.get("premises"):
            s = states[evidence_id(record["id"])]
            require(not s["stale"], "new derivation has withdrawn/stale premises")
    return {"snapshot": after, "delta": lineage_delta(before, after), "authority": "none"}
