import copy
import pytest
from omegaatom.envelope import validate,parse_evidence_ref
from omegareason.publication_plan import prepare_batch
from omegareason.bound_worker import mark_advice
from omegareason.qualify_bridge import source
from omegareason.atom_bridge import infer_snapshot

@pytest.fixture
def snapshots():
    base={'version':'0.1','owner':'lab','scope':'synthetic-atom','revision':1,'records':[
        source(1,['Inheritance','alpha','beta'],['stv',.8,.7]),source(2,['Inheritance','beta','gamma'],['stv',.8,.7])]}
    candidate=infer_snapshot(base,'nal')['snapshot']
    old={tuple(r['id']) for r in base['records']}
    return base,mark_advice(candidate,[r['id'] for r in candidate['records'] if tuple(r['id']) not in old])

def test_retries_deterministic_and_no_host_identity_mint(snapshots):
    base,candidate=snapshots
    one=prepare_batch(base,candidate)
    assert one==prepare_batch(base,copy.deepcopy(candidate))
    assert one['authority']=='none' and one['facts']
    assert len({f['idempotency_key'] for f in one['facts']})==len(one['facts'])
    for f in one['facts']:
        assert 'id' not in f['payload'] and 'stamp' not in f['payload']
        for ref in [f['local_ref'],*f['payload']['premise_refs']]:parse_evidence_ref(ref)

def test_unknown_truth_omitted_and_status_restrictions_preserved(snapshots):
    base,candidate=snapshots;prepared=prepare_batch(base,candidate)
    unknown=[f['payload'] for f in prepared['facts'] if f['payload']['unknown']]
    assert unknown and {p['statement'][0] for p in unknown}=={'AdmissionState','Restriction'}
    assert all('f' not in p and 'c' not in p for p in unknown)
    assert all(p['status']=='inferred' for p in unknown)

def test_payload_change_changes_key_and_history_rewrite_refused(snapshots):
    base,candidate=snapshots
    one=prepare_batch(base,candidate)
    changed=copy.deepcopy(candidate)
    next(r for r in changed['records'] if r['source']['owner']=='omegareason' and not r['unknown'])['truth'][1]=.2
    two=prepare_batch(base,changed)
    assert one['batch_key']!=two['batch_key']
    rewritten=copy.deepcopy(candidate);rewritten['records'][0]['truth'][1]=.3
    with pytest.raises(ValueError,match='rewritten'):prepare_batch(base,rewritten)

def test_scope_binding_and_missing_closure_refused(snapshots):
    base,candidate=snapshots
    changed=copy.deepcopy(candidate);changed['scope']='other-scope'
    for r in changed['records']:r['scope']='other-scope'
    with pytest.raises(ValueError,match='frozen base'):prepare_batch(base,changed)
    missing=copy.deepcopy(candidate);missing['records'].pop(0)
    with pytest.raises(ValueError,match='lineage|stamp'):prepare_batch(base,missing)
