"""Synthetic data vectors for host S1/S1b integration; never host authority."""
import copy
import json
from .e1 import fixture, control
from .envelope import digest, sidecars, Refused
from .transitions import stage_append


def vectors():
    base, ids, _ = fixture()
    withdrawal = control(["ev", "atom-control", 1], ids["failure"], 1, 10)
    withdrawn = stage_append(base, [withdrawal], expected_revision=base["revision"], expected_digest=digest(base))["snapshot"]
    restored_control = control(["ev", "atom-control", 2], withdrawal["id"], 2, 20)
    unknown = copy.deepcopy(base["records"][-1])
    unknown.update(id=["ev", "swarm-b", 2], stamp=[["ev", "swarm-b", 2]], unknown=True,
                   statement=["SyntheticUnknown", "unmeasured"])
    unknown.pop("truth")
    unknown["source"].update(subject="unmeasured", digest=digest(["unmeasured"]))
    cases = []
    def add(name, before, batch, *, revision=None, refused=False):
        args = {"expected_revision": before["revision"] if revision is None else revision,
                "expected_digest": digest(before)}
        case = {"name": name, "before": copy.deepcopy(before), "batch": copy.deepcopy(batch), "binding": args}
        try:
            result = stage_append(before, batch, **args)
        except Refused:
            if not refused:
                raise
            case["expected"] = {"outcome": "refused"}
        else:
            if refused:
                raise AssertionError("negative vector accepted: " + name)
            case["expected"] = {"outcome": "staged", "snapshot_digest": digest(result["snapshot"]),
                                "delta": result["delta"], "sidecars": sidecars(result["snapshot"])}
        cases.append(case)
    add("withdrawal-five-descendants", base, [withdrawal])
    add("restore-via-control-retraction", withdrawn, [restored_control])
    add("unknown-without-asserted-truth", base, [unknown])
    invalid = copy.deepcopy(unknown)
    invalid["truth"] = ["stv", 0.5, 0]
    add("unknown-with-invented-truth", base, [invalid], refused=True)
    add("stale-base-revision", base, [withdrawal], revision=0, refused=True)
    duplicate = copy.deepcopy(base["records"][0])
    duplicate.update(id=["ev", "swarm-a", 2], stamp=[["ev", "swarm-a", 2]])
    add("duplicate-read-new-id", base, [duplicate], refused=True)
    derived = copy.deepcopy(base["records"][1])
    derived["id"] = ["ev", "reason", 2]
    derived["source"].update(subject="fresh-hypothesis", digest=digest(["fresh-hypothesis"]))
    add("new-derivation-on-withdrawn-source", withdrawn, [derived], refused=True)
    add("same-batch-withdrawal-and-new-derivation", base, [withdrawal, derived], refused=True)
    return {"schema": "omegaatom/host-conformance/1", "envelope_version": "0.1", "authority": "none", "cases": cases,
            "limits": ["synthetic manual lineage", "caller ids model already-host-allocated records only",
                       "no source authentication, grant, atomic commit or durable replay tested",
                       "expected staging is not host integration or admission approval"]}


if __name__ == "__main__":
    print(json.dumps(vectors(), sort_keys=True, separators=(",", ":")))
