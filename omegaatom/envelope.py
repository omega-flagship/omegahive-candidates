"""D2 evidence sidecars. No evaluator, imports, I/O, grants, or space writes.

JSON is a transport projection of atom data, not a new belief representation.
The host supplies custody/authentication separately.
"""
import copy
import hashlib
import json
import math
import re
from collections import deque

STATUSES = {"observed", "inferred", "hypothetical", "predicted", "interventional", "simulated", "borrowed-prior"}
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/@+-]{0,127}\Z")
FORBIDDEN = {"!", "=", "import!", "bind!", "add-atom", "remove-atom", "eval", "evalc", "call", "py-call", "py-dot"}
MAX_RECORDS = 1000


class Refused(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Refused(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def identifier(value):
    require(isinstance(value, str) and TOKEN.fullmatch(value), "invalid exact identifier")
    return value


def evidence_id(value):
    require(isinstance(value, list) and len(value) == 3 and value[0] == "ev", "evidence id must be [ev, owner, sequence]")
    identifier(value[1])
    require(type(value[2]) is int and 0 < value[2] <= 2**63 - 1, "evidence sequence must be positive signed-64-bit integer")
    return tuple(value)


def format_evidence_ref(value):
    """Canonical external reference; structured ev atom remains authoritative."""
    _, owner, sequence = evidence_id(value)
    return f"ev:{owner}:{sequence}"


def parse_evidence_ref(value):
    """Exact parser, never a query pattern. Owner may contain literal colons."""
    require(isinstance(value, str) and len(value) <= 160 and value.startswith("ev:"), "invalid evidence reference")
    parts = value[3:].rsplit(":", 1)
    require(len(parts) == 2 and re.fullmatch(r"[1-9][0-9]*", parts[1]), "noncanonical evidence sequence")
    result = ["ev", parts[0], int(parts[1])]
    evidence_id(result)
    require(format_evidence_ref(result) == value, "noncanonical evidence reference")
    return result


def inert_atom(value, depth=0):
    require(depth <= 32, "atom depth bound exceeded")
    if isinstance(value, list):
        require(len(value) <= 256, "atom width bound exceeded")
        if value:
            require(not (isinstance(value[0], str) and value[0] in FORBIDDEN), "executable atom refused")
        for item in value:
            inert_atom(item, depth + 1)
    elif isinstance(value, str):
        require(len(value) <= 4096 and not value.startswith(("!", "$", "&")), "executable/variable/raw-handle text refused")
    else:
        require(type(value) in (int, float) and math.isfinite(value), "atom contains non-data value")


def truth(value):
    require(isinstance(value, list) and len(value) == 3 and value[0] == "stv", "truth must be [stv, frequency, confidence]")
    f, c = value[1:]
    require(type(f) in (int, float) and type(c) in (int, float) and math.isfinite(f) and math.isfinite(c), "non-finite truth")
    require(0 <= f <= 1 and 0 <= c < 1, "truth out of bounds")


def validate(snapshot):
    try:
        require(len(canonical(snapshot).encode()) <= 2_000_000, "snapshot byte bound exceeded")
    except (TypeError, ValueError, RecursionError) as error:
        raise Refused(str(error)) from error
    require(isinstance(snapshot, dict) and set(snapshot) == {"version", "owner", "scope", "revision", "records"}, "snapshot fields mismatch")
    require(snapshot["version"] == "0.1", "unsupported envelope version")
    identifier(snapshot["owner"])
    identifier(snapshot["scope"])
    require(type(snapshot["revision"]) is int and snapshot["revision"] >= 0, "invalid snapshot revision")
    records = snapshot["records"]
    require(isinstance(records, list) and len(records) <= MAX_RECORDS, "record bound exceeded")
    index, source_reads = {}, {}
    required = {"id", "statement", "source", "status", "scope", "stamp", "unknown"}
    optional = {"truth", "premises", "rule", "retention"}
    for record in records:
        require(isinstance(record, dict) and required <= set(record) <= required | optional, "record fields mismatch")
        key = evidence_id(record["id"])
        require(key not in index, "duplicate evidence identity")
        index[key] = record
        inert_atom(record["statement"])
        require(isinstance(record["statement"], list) and record["statement"], "statement must be a nonempty atom expression")
        require(isinstance(record["status"], str) and record["status"] in STATUSES, "unsupported epistemic status")
        identifier(record["scope"])
        require(record["scope"] == snapshot["scope"], "foreign scope requires a host-granted projection")
        source = record["source"]
        require(isinstance(source, dict) and set(source) == {"owner", "subject", "revision", "digest"}, "Source fields mismatch")
        identifier(source["owner"])
        identifier(source["subject"])
        require(key[1] == source["owner"], "evidence issuer differs from Source owner")
        require(type(source["revision"]) is int and source["revision"] >= 0, "invalid source revision")
        require(isinstance(source["digest"], str) and re.fullmatch(r"[a-f0-9]{64}", source["digest"]), "invalid source digest")
        require(type(record["unknown"]) is bool, "unknown must be explicit boolean")
        require(not record["unknown"] or "truth" not in record, "unknown cannot carry invented truth")
        require(record["unknown"] or "truth" in record, "known record requires truth")
        if "truth" in record:
            truth(record["truth"])
        stamp = record["stamp"]
        require(isinstance(stamp, list) and 0 < len(stamp) <= MAX_RECORDS, "stamp must be nonempty and bounded")
        stamp_keys = [evidence_id(e) for e in stamp]
        require(len(set(stamp_keys)) == len(stamp_keys), "duplicate stamp member")
        require(stamp_keys == sorted(stamp_keys), "stamp must be sorted")
        premises = record.get("premises", [])
        require(isinstance(premises, list) and len(premises) <= MAX_RECORDS, "invalid premises")
        premise_keys = [evidence_id(e) for e in premises]
        require(len(set(premise_keys)) == len(premise_keys), "duplicate premise")
        require(record["status"] != "inferred" or premises, "inferred atom missing premises")
        require(bool(premises) == ("rule" in record), "derived atoms require premises and rule together")
        if premises:
            require(isinstance(record["rule"], list) and len(record["rule"]) == 2, "rule requires identity and version")
            for part in record["rule"]:
                identifier(part)
        else:
            require(stamp_keys == [key], "source evidence must have its own exact stamp")
            if record["status"] == "observed" and not record["unknown"]:
                require(record["truth"][2] == 0.5, "single observation confidence must be 0.5")
            read_key = canonical([source, record["statement"], record["scope"]])
            require(read_key not in source_reads, "duplicate source read is not new evidence")
            source_reads[read_key] = key
        retention = record.get("retention", {})
        require(isinstance(retention, dict) and set(retention) <= {"protected", "expires_at"}, "invalid retention")
        require(type(retention.get("protected", False)) is bool, "invalid protected flag")
        if "expires_at" in retention:
            require(type(retention["expires_at"]) in (int, float) and math.isfinite(retention["expires_at"]) and retention["expires_at"] >= 0, "invalid expiry")
        if record["statement"][0] == "Retracted":
            stmt = record["statement"]
            require(len(stmt) == 5 and record["status"] == "observed" and not premises and not record["unknown"], "retraction must be known source observation evidence")
            evidence_id(stmt[1])
            require(isinstance(stmt[2], str) and bool(stmt[2]), "retraction reason required")
            identifier(stmt[3])
            require(type(stmt[4]) in (int, float) and math.isfinite(stmt[4]) and stmt[4] >= 0, "invalid retraction time")
    for key, record in index.items():
        premises = [evidence_id(e) for e in record.get("premises", [])]
        for p in premises:
            require(p in index, "missing premise: incomplete lineage")
            require(p != key, "self premise")
        if premises:
            union = set().union(*(set(evidence_id(e) for e in index[p]["stamp"]) for p in premises))
            require(set(evidence_id(e) for e in record["stamp"]) == union, "derived stamp must equal complete premise stamp union")
        else:
            require(all(evidence_id(e) in index for e in record["stamp"]), "unresolved stamp")
        if record["statement"][0] == "Retracted":
            target = evidence_id(record["statement"][1])
            require(target in index and target != key, "retraction target missing or self")
    # Longest depth must not depend on record order or memoised traversal paths.
    _topology(index)
    return copy.deepcopy(snapshot)


def _topology(index):
    """Parents first, accounting for both premise and control edges."""
    pending, children, depth = {}, {}, {}
    for key, r in index.items():
        parents = {evidence_id(p) for p in r.get("premises", [])}
        if r["statement"][0] == "Retracted":
            parents.add(evidence_id(r["statement"][1]))
        pending[key] = len(parents)
        depth[key] = 1
        for parent in parents:
            children.setdefault(parent, []).append(key)
    ready = deque(k for k in index if pending[k] == 0)
    ordered = []
    while ready:
        key = ready.popleft()
        ordered.append(key)
        require(depth[key] <= 128, "lineage depth bound exceeded")
        for child in children.get(key, []):
            depth[child] = max(depth[child], depth[key] + 1)
            pending[child] -= 1
            if not pending[child]:
                ready.append(child)
    require(len(ordered) == len(index), "cyclic evidence graph")
    return ordered


def dumps(snapshot):
    return canonical(validate(snapshot))


def loads(text):
    require(isinstance(text, str) and len(text.encode()) <= 2_000_000, "snapshot byte bound exceeded")
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(Refused("non-finite JSON")))
    except (ValueError, RecursionError) as error:
        raise Refused(str(error)) from error
    return validate(value)


def sidecars(snapshot):
    """Return inert atom trees. Consumer must add as data, NEVER import/eval."""
    snapshot = validate(snapshot)
    atoms = []
    for r in snapshot["records"]:
        e, s = r["id"], r["source"]
        atoms.extend([["Source", e, s["owner"], s["subject"], s["revision"], s["digest"]],
                      ["Status", e, r["status"]], ["Scope", e, r["scope"]],
                      ["Statement", e, r["statement"]], ["Stamp", e, r["stamp"]]])
        if not r["unknown"]:
            # Existing Asserted/Current statement, tv, stamp shapes are unchanged.
            atoms.append(["Asserted", s["owner"], r["statement"], r["truth"], r["stamp"]])
        if r.get("premises"):
            atoms.append(["Premises", e, r["premises"], ["Rule", *r["rule"]]])
        if r["statement"][0] == "Retracted":
            atoms.append(r["statement"])
    return copy.deepcopy(atoms)


def lineage_state(snapshot):
    snapshot = validate(snapshot)
    index = {evidence_id(r["id"]): r for r in snapshot["records"]}
    retractors = {}
    for key, r in index.items():
        if r["statement"][0] == "Retracted":
            retractors.setdefault(evidence_id(r["statement"][1]), []).append(key)
    ordered = _topology(index)
    active, causes = {}, {}
    for key in reversed(ordered):
        active[key] = not any(active[e] for e in retractors.get(key, []))
    for key in ordered:
        result = set()
        for p in index[key].get("premises", []):
            parent = evidence_id(p)
            if not active[parent]:
                result.add(parent)
            result.update(causes[parent])
        causes[key] = result
    return [{"id": list(k), "retracted": not active[k], "stale": bool(causes[k]),
             "causes": [list(p) for p in sorted(causes[k])]} for k in sorted(index)]


def revision_allowed(left, right):
    """Eligibility only; numerical truth revision remains lib_hive-owned."""
    return not set(evidence_id(e) for e in left) & set(evidence_id(e) for e in right)
