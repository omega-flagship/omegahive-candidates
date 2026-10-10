import copy
import pytest
from omegalearn import Ledger, Refused, digest
from omegalearn.experiment import run

def event():
    return dict(schema='omegalearn/event/1',id='a/episode-1',owner='source-owner',scope='swarm-a',
        subject=dict(id='export-1',revision='r1',digest='a'*64),evidence_refs=['atom/ev-1'],predictions=[],assumptions=[],
        review_findings=[],outcome_refs=[],corrections=[],permissions=dict(audiences=['learn','recipient'],derive=True,redistribute=True),
        payload=dict(kind='error',data={'text':'(bad input'}))

def resolver(e):
    return dict(current_subject=e['subject'],owner=e['owner'],scope=e['scope'],permissions=e['permissions'],
                visible_refs=e['evidence_refs'],references_valid=True)

def package(e):
    p=dict(schema='omegalearn/package/1',id='repair',version='1',kind='skill',owner='learn-owner',scope='learn',source_events=[e['id']],
           evidence_refs=e['evidence_refs'],provenance_refs=[],evaluation_refs=['evaluation/synthetic'],
           runtime=dict(requires=['omegalearn:0.1'],entrypoint='repair.apply'),rollback=None,content=run()['skill'])
    return dict(p,digest=digest(p))

def setup():
    l=Ledger();e=event();l.admit(e,resolver);return l,e,l.propose(package(e))

def test_duplicate_conflict_alias_and_copy():
    l=Ledger();e=event();assert l.admit(e,resolver)['new_evidence']
    assert not l.admit(e,lambda _:None)['new_evidence']
    alias=copy.deepcopy(e);alias['id']='different'
    with pytest.raises(Refused):l.admit(alias,resolver)
    changed=copy.deepcopy(e);changed['payload']['data']='changed'
    with pytest.raises(Refused):l.admit(changed,resolver)
    e['payload']['data']='caller mutation'
    assert l.checkpoint()['events']['a/episode-1']['payload']['data']!="caller mutation"

@pytest.mark.parametrize('change',[{'current_subject':None},{'owner':'other'},{'permissions':{}},{'visible_refs':[]},{'references_valid':False}])
def test_trusted_resolution_required(change):
    l=Ledger();e=event()
    with pytest.raises(Refused):l.admit(e,lambda x:dict(resolver(x),**change))

def test_authority_fields_refused_and_text_inert():
    l=Ledger();e=event();e['payload']['data']={'code':'(progn (delete-all))'}
    l.admit(e,resolver)
    e['grant_admin']=True
    with pytest.raises(Refused):l.admit(e,resolver)

def test_provenance_immutable_package_and_rollback():
    l,e,k=setup();p=package(e);p['evidence_refs']=[];p['digest']=digest({x:v for x,v in p.items() if x!='digest'})
    with pytest.raises(Refused):l.propose(p)
    p=package(e);p['content']['rules']=['changed'];p['digest']=digest({x:v for x,v in p.items() if x!='digest'})
    with pytest.raises(Refused):l.propose(p)
    p=package(e);p['version']='2';p['rollback']={'id':'repair','version':'1','digest':l.package(k)['digest']};p['digest']=digest({x:v for x,v in p.items() if x!='digest'})
    assert l.propose(p)=='repair@2'

def test_retraction_delivery_and_restart():
    l,e,k=setup();row=l.deliver(k,'recipient','artifact/r1',lambda *_:True)
    assert row['states']['delivered'] and all(row['states'][s] is None for s in row['states'] if s!='delivered')
    with pytest.raises(Refused):l.record_delivery_state(0,'measured-useful','unverified',lambda *_:False)
    l.record_delivery_state(0,'acknowledged','recipient/ack',lambda *_:True)
    with pytest.raises(Refused):l.invalidate(e['id'],lambda _:False)
    l.invalidate(e['id'],lambda _:True)
    restored=Ledger.restore(l.checkpoint());assert restored.package(k)['local_status']=='stale'
    with pytest.raises(Refused):restored.deliver(k,'recipient','artifact/r2',lambda *_:True)
    corrupted=l.checkpoint();corrupted['stale']=[]
    with pytest.raises(Refused):Ledger.restore(corrupted)

def test_corrected_source_invalidates():
    l,e,k=setup();new=copy.deepcopy(e);new['id']='a/correction';new['subject']['revision']='r2';new['subject']['digest']='b'*64;new['corrections']=[e['id']]
    l.admit(new,resolver);assert l.package(k)['local_status']=='stale'

def test_redistribution_refused():
    l,e,k=setup()
    with pytest.raises(Refused):l.deliver(k,'outside','artifact/r1',lambda *_:True)
    with pytest.raises(Refused):l.deliver(k,'recipient','artifact/r1',lambda *_:False)

def test_actual_synthetic_transfer_and_masked_controls():
    r=run();assert r['arms']['FULL']['correct']==7
    assert r['arms']['typed-memory']['correct']==4
    assert r['arms']['SHAM']['correct']==r['arms']['SEVERED']['correct']==4
    assert all(arm['model_calls']==0 for arm in r['arms'].values())

def test_same_evidence_in_another_export_is_not_new():
    l=Ledger();e=event();l.admit(e,resolver)
    second=copy.deepcopy(e);second['id']='export-two';second['subject']['id']='export-two'
    assert l.admit(second,resolver)['new_evidence'] is False

def test_restore_rollback_chain_independent_of_json_key_order():
    l,e,k=setup()
    for version,parent in [('2','1'),('10','2')]:
        p=package(e);p['version']=version;p['rollback']={'id':'repair','version':parent,'digest':l.package('repair@'+parent)['digest']}
        p['digest']=digest({x:v for x,v in p.items() if x!='digest'});l.propose(p)
    restored=Ledger.restore(l.checkpoint())
    assert restored.package('repair@10')['rollback']['version']=='2'
