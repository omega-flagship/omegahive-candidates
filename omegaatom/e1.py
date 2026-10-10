"""Atom-only E1 preparation. Manual synthetic lineage; no cognitive claim."""
import copy
import json
import subprocess
import sys
from pathlib import Path
from .envelope import validate, digest, dumps, lineage_state, format_evidence_ref
from .transitions import stage_append


def fixture():
    ids = {name: ["ev", owner, 1] for name, owner in [
        ("failure", "swarm-a"), ("hypothesis", "reason"), ("repair", "learn"),
        ("plan", "planner"), ("candidate", "code"), ("review", "review"),
        ("independent", "swarm-b")]}
    # Evaluator-authored oracle, declared separately from the subject walk.
    expected = {"failure": [], "hypothesis": ["failure"], "repair": ["hypothesis"],
                "plan": ["repair"], "candidate": ["plan"], "review": ["candidate"], "independent": []}
    records = []
    for name, parents in expected.items():
        identifier = ids[name]
        r = {"id": identifier, "statement": ["E1Fixture", name],
             "source": {"owner": identifier[1], "subject": name, "revision": 1, "digest": digest(["fixture", name])},
             "status": "inferred" if parents else "simulated", "scope": "synthetic-e1-projection",
             "stamp": [ids["failure"]] if parents else [identifier], "unknown": False, "truth": ["stv", 0.8, 0.5]}
        if parents:
            r.update(premises=[ids[p] for p in parents], rule=["manual-fixture-link", "0.1"])
        records.append(r)
    records[-1]["retention"] = {"protected": True}
    return validate({"version": "0.1", "owner": "synthetic-evaluator", "scope": "synthetic-e1-projection", "revision": 1, "records": records}), ids, expected


def control(identifier, target, revision, time):
    return {"id": identifier, "statement": ["Retracted", target, "synthetic correction", "synthetic-evaluator", time],
            "source": {"owner": identifier[1], "subject": "control-" + str(identifier[2]), "revision": revision,
                       "digest": digest([identifier, target, time])}, "status": "observed", "scope": "synthetic-e1-projection",
            "stamp": [identifier], "unknown": False, "truth": ["stv", 1, 0.5]}


def _append(snapshot, records):
    return stage_append(snapshot, records, expected_revision=snapshot["revision"], expected_digest=digest(snapshot))


def reconstruct(snapshot):
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, "-B", "-m", "omegaatom.reconstruct"],
                            input=dumps(snapshot), text=True, capture_output=True, cwd=root,
                            env={"PYTHONPATH": str(root), "PYTHONDONTWRITEBYTECODE": "1"}, timeout=10)
    if result.returncode:
        raise RuntimeError("data reconstruction failed: " + result.stderr)
    restored = json.loads(result.stdout)
    if restored["snapshot_digest"] != digest(snapshot):
        raise RuntimeError("reconstruction digest mismatch")
    return restored


def qualify():
    from omegabench.correction import score_withdrawal
    snapshot, ids, graph = fixture()
    withdrawal = control(["ev", "atom-control", 1], ids["failure"], 1, 10)
    staged = _append(snapshot, [withdrawal])
    after = staged["snapshot"]
    restarted = reconstruct(after)
    index = {tuple(v): k for k, v in ids.items()}
    def usability(states):
        return {format_evidence_ref(s["id"]): not (s["stale"] or s["retracted"])
                for s in states if tuple(s["id"]) in index}
    oracle = {format_evidence_ref(ids[k]): [format_evidence_ref(ids[p]) for p in parents] for k, parents in graph.items()}
    scored = score_withdrawal(oracle, format_evidence_ref(ids["failure"]),
                             usability(lineage_state(after)), usability(restarted["states"]),
                             protected=[format_evidence_ref(ids["independent"])])
    restored = _append(after, [control(["ev", "atom-control", 2], withdrawal["id"], 2, 20)])
    expected_stale = [ids[n] for n in ("hypothesis", "repair", "plan", "candidate", "review")]
    assert sorted(staged["delta"]["newly_stale"]) == sorted(expected_stale)
    assert scored["score"] == 1 and not scored["adoption_authorized"]
    assert sorted(restored["delta"]["newly_eligible"]) == sorted([ids["failure"], *expected_stale])
    fresh = copy.deepcopy(snapshot["records"][0])
    fresh["id"] = ["ev", "swarm-a", 2]
    fresh["stamp"] = [fresh["id"]]
    fresh["source"].update(revision=2, digest=digest(["fixture", "corrected-failure"]))
    corrected = _append(after, [fresh])
    assert sorted(s["id"] for s in lineage_state(corrected["snapshot"]) if s["stale"]) == sorted(expected_stale)
    return {"level": "L0", "scope": "Atom-only E1 preparation over manual synthetic single-scope projection",
            "oracle_digest": digest(oracle), "withdrawal_delta": staged["delta"], "restore_delta": restored["delta"],
            "fresh_source_does_not_revive_old_derivations": True,
            "fresh_process_snapshot_digest": restarted["snapshot_digest"], "bench_fixture_score": scored,
            "limits": ["manual lineage, no Reason/Learn/Planner/Code/Review execution", "source labels are not actual two-swarm grants",
                       "fresh Python data reconstruction is not host/interpreter restart", "no S1/S1b, deployment, model or synergy claim"]}
