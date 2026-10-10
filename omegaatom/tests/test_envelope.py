import copy
import json
import pytest
from omegaatom.envelope import Refused, STATUSES, validate, dumps, loads, sidecars, lineage_state, revision_allowed, digest, format_evidence_ref, parse_evidence_ref
from omegaatom.planner import plan, validate_proposal
from omegaatom.seed import adapt_seed
import hashlib


def ev(n):
    return ["ev", "fixture", n]


def record(n, status="observed", unknown=False, premises=None):
    out = {"id": ev(n), "statement": ["Witness", "fixture-" + str(n), "a" * 64],
           "source": {"owner": "fixture", "subject": "source-" + str(n), "revision": 1, "digest": "a" * 64},
           "status": status, "scope": "synthetic-a", "stamp": [ev(n)], "unknown": unknown}
    if not unknown:
        out["truth"] = ["stv", 0.8, 0.5]
    if premises:
        out.update(premises=[ev(p) for p in premises], rule=["integration-proposal", "0.1"])
    return out


def snapshot(records=None):
    return {"version": "0.1", "owner": "fixture", "scope": "synthetic-a", "revision": 1, "records": records or [record(1)]}


def chain():
    a, b, c, independent = record(1), record(2, "inferred", premises=[1]), record(3, "inferred", premises=[2]), record(4)
    b["stamp"] = c["stamp"] = [ev(1)]
    b["statement"] = ["IntegrationProposal", "creative-search", "nars-query", "bounded-inference", a["statement"]]
    return snapshot([a, b, c, independent])


def retract(n, target):
    r = record(n)
    r["statement"] = ["Retracted", ev(target), "source withdrawn", "fixture", 100 + n]
    return r


@pytest.mark.parametrize("status", sorted(STATUSES))
def test_every_status_roundtrip(status):
    r = record(2, status, premises=[1] if status == "inferred" else None)
    records = [record(1), r] if status == "inferred" else [r]
    if status == "inferred":
        r["stamp"] = [ev(1)]
    s = snapshot(records)
    assert loads(dumps(s)) == s


def test_unknown_has_no_truth_and_no_asserted_tv():
    s = snapshot([record(1, "hypothetical", True)])
    assert loads(dumps(s)) == s
    assert not any(a[0] == "Asserted" for a in sidecars(s))
    s["records"][0]["truth"] = ["stv", 0.5, 0.0]
    with pytest.raises(Refused, match="invented"):
        validate(s)


def test_missing_premises_refused():
    with pytest.raises(Refused, match="missing premises"):
        validate(snapshot([record(1, "inferred")]))


def test_incomplete_union_and_missing_premise_refused():
    s = chain()
    s["records"][2]["stamp"] = [ev(2)]
    with pytest.raises(Refused, match="union"):
        validate(s)
    s = chain()
    s["records"][2]["premises"] = [ev(99)]
    with pytest.raises(Refused, match="missing premise"):
        validate(s)


def test_overlap_blocks_revision():
    assert not revision_allowed([ev(1)], [ev(1), ev(2)])
    assert revision_allowed([ev(1)], [ev(2)])


def test_exact_transitive_descendants_and_restore():
    s = chain()
    s["records"].append(retract(5, 1))
    states = {tuple(r["id"]): r for r in lineage_state(s)}
    assert {k for k, r in states.items() if r["stale"]} == {tuple(ev(2)), tuple(ev(3))}
    assert states[tuple(ev(1))]["retracted"]
    assert not states[tuple(ev(4))]["stale"]
    s["records"].append(retract(6, 5))
    assert not any(r["stale"] for r in lineage_state(s))
    assert not next(r for r in lineage_state(s) if r["id"] == ev(1))["retracted"]
    # Independent withdrawal still prevents restoration.
    s["records"].append(retract(7, 1))
    assert {tuple(r["id"]) for r in lineage_state(s) if r["stale"]} == {tuple(ev(2)), tuple(ev(3))}


def test_duplicate_source_read_does_not_mint_evidence():
    a = record(1)
    duplicate = copy.deepcopy(a)
    duplicate.update(id=ev(2), stamp=[ev(2)], status="borrowed-prior")
    with pytest.raises(Refused, match="duplicate source read"):
        validate(snapshot([a, duplicate]))


@pytest.mark.parametrize("bad", [["ev", "%", 1], ["ev", "fixture", True], ["ev", "fixture", "1"], ["ev", "_", 1], "ev:*", ["ev", "fixture", 0], ["ev", "fixture", 2**63]])
def test_invalid_exact_ids_refused(bad):
    s = snapshot()
    s["records"][0]["id"] = bad
    with pytest.raises(Refused):
        validate(s)


@pytest.mark.parametrize("atom", [["!", ["import!", "evil"]], ["Thing", ["add-atom", "self", "x"]], ["=", ["f"], ["x"]], ["Thing", "$wildcard"], ["Thing", "&self"]])
def test_executable_snapshot_refused(atom):
    s = snapshot()
    s["records"][0]["statement"] = atom
    with pytest.raises(Refused):
        validate(s)


def test_raw_metta_import_refused_by_data_decoder():
    with pytest.raises(Refused):
        loads('!(import! &self "memory.metta")')


def test_cycles_scope_and_truth_refused():
    s = chain()
    s["records"][0].update(status="inferred", premises=[ev(3)], rule=["cycle", "0.1"])
    with pytest.raises(Refused, match="cyclic"):
        validate(s)
    for change in ({"scope": "synthetic-b"}, {"truth": ["stv", 0.5, float("nan")]}, {"truth": ["stv", 0.5, 1.0]}):
        s = snapshot()
        s["records"][0].update(change)
        with pytest.raises(Refused):
            validate(s)


def test_duplicate_json_keys_refused():
    with pytest.raises(Refused, match="duplicate JSON"):
        loads('{"version":"0.1","version":"0.2"}')


def test_concrete_underscored_owner_is_literal_not_a_pattern():
    r = record(1)
    r["id"] = ["ev", "agent_1", 1]
    r["stamp"] = [r["id"]]
    r["source"]["owner"] = "agent_1"
    assert validate(snapshot([r]))["records"][0]["id"] == ["ev", "agent_1", 1]


def test_direct_api_byte_and_type_bounds():
    s = snapshot()
    s["records"][0]["statement"] = ["Payload", "x" * 2_000_001]
    with pytest.raises(Refused, match="byte bound"):
        validate(s)
    s = snapshot()
    s["records"][0]["statement"] = object()
    with pytest.raises(Refused):
        validate(s)


@pytest.mark.parametrize("owner", ["fixture", "agent_1", "org:agent", "my-swarm", "agent@hive"])
def test_canonical_evidence_reference_roundtrip(owner):
    atom = ["ev", owner, 12]
    assert parse_evidence_ref(format_evidence_ref(atom)) == atom


@pytest.mark.parametrize("ref", ["ev:fixture:01", "ev:fixture:0", "ev:fixture:-1", "ev:fixture:+1", "ev:fixture:1.0", "ev:%:1", "ev:_:1", "ev:$x:1", "ev:fixture:*", "ev:fixture:1 ", " ev:fixture:1", "ev::1", "EV:fixture:1", "ev:fixture", "ev:fixture:9223372036854775808", None])
def test_noncanonical_evidence_refs_refused(ref):
    with pytest.raises(Refused):
        parse_evidence_ref(ref)


def test_existing_asserted_shape_and_sidecar_ancestry():
    s = chain()
    atoms = sidecars(s)
    r = s["records"][1]
    assert ["Asserted", "fixture", r["statement"], r["truth"], r["stamp"]] in atoms
    assert ["Premises", ev(2), [ev(1)], ["Rule", "integration-proposal", "0.1"]] in atoms
    atoms.clear()
    assert s == chain()


def test_effect_statement_is_data_and_never_authority():
    s = snapshot([record(1, "hypothetical", True)])
    s["records"][0]["statement"] = ["Effect", "repair-rule", "reduces-error"]
    assert validate(s) == s
    assert not any(a[0] in {"Grant", "Permit"} for a in sidecars(s))


def test_planner_staleness_retention_and_binding():
    s = chain()
    for r in s["records"]:
        r["retention"] = {"expires_at": 1}
    s["records"][3]["retention"]["protected"] = True
    before = copy.deepcopy(s)
    proposals = plan(s, now=2)
    assert s == before
    assert next(p for p in proposals if p["targets"] == [ev(1)])["action"] == "retain"
    assert next(p for p in proposals if p["targets"] == [ev(4)])["action"] == "retain"
    assert next(p for p in proposals if p["targets"] == [ev(3)])["action"] == "archive-candidate"
    for p in proposals:
        assert validate_proposal(p, s) == p
    s["revision"] += 1
    with pytest.raises(Refused, match="stale"):
        validate_proposal(proposals[0], s)
    s = before
    s["records"].append(retract(5, 1))
    proposals = plan(s, now=2)
    assert {tuple(p["targets"][0]) for p in proposals if p["action"] == "mark-stale"} == {tuple(ev(2)), tuple(ev(3))}


def test_proposal_tamper_refused():
    s = snapshot()
    s["records"][0]["retention"] = {"expires_at": 1}
    p = plan(s, 2)[0]
    p["authority"] = "execute"
    p["id"] = digest({k: v for k, v in p.items() if k != "id"})
    with pytest.raises(Refused, match="authority"):
        validate_proposal(p, s)


def test_seed_wrappers_are_unwrapped_as_data_and_hash_checked():
    text = '; seed\n!(bind! &omega-knowledge (new-space))\n!(add-atom &omega-knowledge (Provides nars-query bounded-inference reasoning))\n'
    pin = hashlib.sha256(text.encode()).hexdigest()
    seed = adapt_seed({"knowledge.metta": {"text": text, "digest": pin}})
    assert seed["records"][0]["statement"] == ["Provides", "nars-query", "bounded-inference", "reasoning"]
    assert seed["records"][0]["unknown"]
    assert "truth" not in seed["records"][0]
    with pytest.raises(Refused, match="drift"):
        adapt_seed({"knowledge.metta": {"text": text + '; changed', "digest": pin}})


@pytest.mark.parametrize("text", ['!(import! &self "evil")', '!(bind! &omega-knowledge (evil))', '!(bind! &omega-knowledge (new-space))\n!(add-atom &omega-knowledge (= (evil) (run)))'])
def test_seed_import_and_executable_payload_refused(text):
    with pytest.raises(Refused):
        adapt_seed({"seed.metta": {"text": text, "digest": hashlib.sha256(text.encode()).hexdigest()}})


@pytest.mark.parametrize("owner", ["org:department:agent", "org:", "a" * 128])
def test_codec_preserves_colons_and_maximum_identity(owner):
    atom = ["ev", owner, 2**63 - 1]
    ref = format_evidence_ref(atom)
    assert ref == "ev:" + owner + ":9223372036854775807"
    assert parse_evidence_ref(ref) == atom
    assert format_evidence_ref(parse_evidence_ref(ref)) == ref


@pytest.mark.parametrize("suffix", ["00", "0012", "12e0", "12.0", "+12", "-12", "１２", "١٢", "12\n", "12\t"])
def test_colon_owner_does_not_relax_numeric_canonicality(suffix):
    with pytest.raises(Refused):
        parse_evidence_ref("ev:org:agent:" + suffix)


@pytest.mark.parametrize("sequence", [True, False, 1.0, "1", 0, -1, 2**63])
def test_formatter_refuses_non_integer_or_out_of_range_sequence(sequence):
    with pytest.raises(Refused):
        format_evidence_ref(["ev", "org:agent", sequence])
