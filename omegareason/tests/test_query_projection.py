import copy
import pytest
from omegaatom.envelope import validate,lineage_state
from omegaatom.projection import project_pages
from omegaatom.transitions import stage_append
from omegaatom.envelope import digest
from omegareason.query_projection import join_pages,project_and_reason
from omegareason.qualify_bridge import source

@pytest.fixture
def base():
    return {'version':'0.1','owner':'lab','scope':'synthetic-atom','revision':1,'records':[
        source(1,['Inheritance','alpha','beta'],['stv',.8,.7]),
        source(2,['Inheritance','beta','gamma'],['stv',.8,.7]),
        source(3,['Inheritance','unrelated','other'],['stv',.8,.7])]}

def event(seq,target,time):
    r=source(seq,['Retracted',target,'synthetic-withdrawal','lab',time],['stv',1,.5])
    r['status']='observed';return r

def append(snapshot,record):
    return stage_append(snapshot,[record],expected_revision=snapshot['revision'],expected_digest=digest(snapshot))['snapshot']

def test_page_join_enables_cross_page_inference_without_scope_join(base):
    out=project_and_reason(base,[r['id'] for r in base['records']],'nal',record_limit=1)
    assert len(out['pages'])==3
    assert any(r['subject']=='alpha' and r['object']=='gamma' for r in out['reason']['native']['results'])

def test_withdrawal_controls_block_inference_and_unrelated_evidence_stays(base):
    withdrawn=append(base,event(10,['ev','lab',1],10))
    out=project_and_reason(withdrawn,[['ev','lab',1],['ev','lab',2],['ev','lab',3]],'nal',record_limit=2)
    joined=join_pages(out['pages'])
    assert any(r['id']==['ev','lab',10] for r in joined['records'])
    assert not any(r['subject']=='alpha' for r in out['reason']['native']['results'])
    state={tuple(r['id']):r for r in lineage_state(joined)}
    assert state[('ev','lab',1)]['retracted'] and not state[('ev','lab',3)]['retracted']

def test_retraction_of_retraction_is_retained_and_restores_eligibility(base):
    withdrawn=append(base,event(10,['ev','lab',1],10))
    restored=append(withdrawn,event(11,['ev','lab',10],20))
    out=project_and_reason(restored,[['ev','lab',1],['ev','lab',2]],'nal',record_limit=3)
    joined=join_pages(out['pages'])
    assert {('ev','lab',10),('ev','lab',11)}<=set(tuple(r['id']) for r in joined['records'])
    assert any(r['subject']=='alpha' and r['object']=='gamma' for r in out['reason']['native']['results'])

def test_overflow_refuses_before_any_inference(base,monkeypatch):
    from omegareason import query_projection as q
    called=[]
    monkeypatch.setattr(q,'infer_snapshot',lambda *args:called.append(True))
    withdrawn=append(base,event(10,['ev','lab',1],10))
    with pytest.raises(ValueError,match='partial lineage'):q.project_and_reason(withdrawn,[['ev','lab',2],['ev','lab',1]],'nal',record_limit=1)
    assert not called

def test_incomplete_groups_mixed_revisions_and_scopes_refused(base):
    pages=project_pages(base,[['ev','lab',1],['ev','lab',2]],record_limit=1)
    for field in ['closure_complete','result_complete']:
        bad=copy.deepcopy(pages);bad[-1][field]=False
        with pytest.raises(ValueError,match='Partial'):join_pages(bad)
    bad=copy.deepcopy(pages);bad[0]['result_complete']=True
    with pytest.raises(ValueError,match='Partial'):join_pages(bad)
    bad=copy.deepcopy(pages);bad[1]['snapshot']['revision']=2
    with pytest.raises(ValueError,match='Mixed'):join_pages(bad)
    bad=copy.deepcopy(pages);bad[1]['snapshot']['scope']='foreign'
    for r in bad[1]['snapshot']['records']:r['scope']='foreign'
    with pytest.raises(ValueError,match='Mixed'):join_pages(bad)

def test_repeated_ancestor_identity_must_match_exactly(base):
    page=project_pages(base,[['ev','lab',1]])[0]
    repeated=[copy.deepcopy(page),copy.deepcopy(page)];repeated[0]['result_complete']=False
    assert len(join_pages(repeated)['records'])==1
    repeated[1]['snapshot']['records'][0]['truth'][1]=.2
    with pytest.raises(ValueError,match='Conflicting'):join_pages(repeated)

def test_controls_and_suppression_survive_fresh_process(base,tmp_path):
    import json,subprocess,sys
    from pathlib import Path
    withdrawn=append(base,event(10,['ev','lab',1],10))
    pages=project_pages(withdrawn,[['ev','lab',1],['ev','lab',2]],record_limit=2)
    path=tmp_path/'closed-pages.json';path.write_text(json.dumps(pages))
    script='''import json,sys
from omegareason.query_projection import join_pages
from omegareason.atom_bridge import infer_snapshot
from omegaatom.envelope import lineage_state
snapshot=join_pages(json.loads(sys.stdin.read()))
print(json.dumps({'states':lineage_state(snapshot),'reason':infer_snapshot(snapshot,'nal')}))
'''
    child=subprocess.run([sys.executable,'-B','-c',script],input=path.read_text(),text=True,capture_output=True,cwd=Path(__file__).resolve().parents[2],timeout=30)
    assert child.returncode==0,child.stderr
    restored=json.loads(child.stdout)
    assert restored['states']==lineage_state(join_pages(pages))
    assert not any(r['subject']=='alpha' for r in restored['reason']['native']['results'])
