"""Explicit isolated host qualification; seeded synthetic identities, no live worker.
Run with the candidate snapshot first on PYTHONPATH. This isn't an IdP test.
"""
import asyncio
import copy
import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from hive.tests.test_core_api import client, agent_headers, FakeSupervisor  # noqa: F401
from hive.tests.test_visibility import person
from hive.core.flows import Flows
from hive.core.hive import Hive
from omegaflow.examples.garden import garden


@pytest.fixture
def setup(client):
    owner=person(client,'u_flow_owner')
    swarm=client.post('/api/swarms',headers=owner,json={'name':'Synthetic garden'}).json()
    worker=client.post('/api/agents',headers=owner,json={'name':'Garden worker','swarm_id':swarm['id']}).json()
    f=garden();es={e['id']:e for e in f['elements']}
    for e in f['elements']:e['meta']['revision_state']='adopted'
    es['submitted']['type']='run.start'
    es['accepted']['type']='goal.done';es['accepted']['props']['source_transition']='t0'
    event=copy.deepcopy(es['accepted']);event['id']='review-done';event['props']['source_transition']='t1';f['elements'].append(event)
    es['t1']['trigger']='accepted';es['t2']['trigger']='review-done';es['t2']['props']['requires_approval']=False
    schema={'type':'object','properties':{'ok':{'type':'boolean'}},'required':['ok'],'additionalProperties':False}
    for tid in ('t0','t1','t2'):
        es[tid]['action']={'kind':'goal','target':swarm['id'],'params':{'title':f'Garden {tid}','assignee':worker['id'],'result_schema':schema,'review':'person' if tid=='t1' else 'none'}}
    out=client.post(f"/api/swarms/{swarm['id']}/flows",headers=owner,json={'title':'Garden flow','body':f,'layout':{'visitor':{'x':10,'y':20}}})
    assert out.status_code==200,out.text
    flow=out.json();prefix=f"/api/flows/{flow['artifact_id']}/revisions/{flow['revision']}"
    return client,owner,swarm,worker,f,flow,prefix


def adopt_start(setup,key='run-1'):
    c,owner,_,_,_,flow,path=setup
    out=c.post(path+'/adopt',headers=owner,json={'digest':flow['digest']});assert out.status_code==200,out.text
    out=c.post(path+'/runs',headers=owner,json={'digest':flow['digest'],'client_key':key});assert out.status_code==200,out.text
    return out.json()


def reconcile(c):asyncio.run(c.app.state.hive.flows.reconcile())


def goal_for(run,tid):return next(s['goal_id'] for s in run['steps'] if s['transition_id']==tid)


def finish(c,worker,gid,proposal=None):
    auth=agent_headers(worker)
    out=c.post(f'/api/agent/goals/{gid}/claim',headers=auth);assert out.status_code==200,out.text
    g=c.get(f'/api/agent/goals/{gid}',headers=auth).json()
    out=c.post(f'/api/agent/goals/{gid}/result',headers=auth,json={'status':'done','result':'synthetic result','data':{'binding_digest':g['binding_digest'],'proposal':proposal if proposal is not None else {'ok':True}}})
    return out


def getrun(setup,rid):
    c,owner,*_=setup
    return c.get('/api/flow-runs/'+rid,headers=owner).json()


def count(c):return c.app.state.hive.db.one("SELECT COUNT(*) AS n FROM goals WHERE id LIKE 'g_flow_%'")['n']


def test_immutable_artifact_and_layout_sidecar(setup):
    c,owner,swarm,worker,f,flow,path=setup
    assert flow['host_digest']=='sha256:'+flow['digest']
    author=c.app.state.hive.db.one('SELECT author FROM artifact_revisions WHERE artifact_id=?',(flow['artifact_id'],))['author']
    assert author=='user:u_flow_owner'
    moved=c.put(path+'/layout',headers=owner,json={'expected_version':1,'layout':{'visitor':{'x':500,'y':20}}}).json()
    assert moved['digest']==flow['digest'] and moved['layout_version']==2
    assert c.put(path+'/layout',headers=owner,json={'expected_version':1,'layout':{}}).status_code==409
    changed=copy.deepcopy(f);changed['elements'][0]['props']['label']='changed'
    nxt=c.post(f"/api/swarms/{swarm['id']}/flows",headers=owner,json={'artifact_id':flow['artifact_id'],'parent':1,'body':changed,'layout':{}}).json()
    assert nxt['revision']==2 and nxt['digest']!=flow['digest']
    assert c.get(path,headers=owner).json()['body']==f
    assert c.post(f"/api/swarms/{swarm['id']}/flows",headers=owner,json={'artifact_id':flow['artifact_id'],'parent':1,'body':f}).status_code==409
    # Same authoritative body is readable through the native C39 artifact API.
    raw=c.get(f"/api/agent/artifacts/{flow['artifact_id']}/revisions/1",headers=agent_headers(worker))
    assert raw.status_code==200,raw.text
    assert json.loads(raw.json()['body'])==f


def test_adoption_and_named_scope_required(setup):
    c,owner,_,worker,_,flow,path=setup
    assert c.post(path+'/runs',headers=owner,json={'digest':flow['digest'],'client_key':'before'}).status_code==409
    assert c.post(path+'/adopt',headers=owner,json={'digest':'a'*64}).status_code==409
    other=person(c,'u_flow_other')
    assert c.get(path,headers=other).status_code==404
    assert c.post(path+'/adopt',headers=other,json={'digest':flow['digest']}).status_code==404
    assert c.post(path+'/adopt',json={'digest':flow['digest']}).status_code==401
    assert c.post(path+'/adopt',headers=agent_headers(worker),json={'digest':flow['digest']}).status_code==401


def test_bound_goal_pipeline_waits_for_result_and_named_review(setup):
    c,owner,_,worker,_,_,_=setup
    run=adopt_start(setup);rid=run['id'];assert count(c)==1
    assert finish(c,worker,goal_for(run,'t0')).json()['status']=='done';reconcile(c);assert count(c)==2
    goal=goal_for(run,'t1');assert finish(c,worker,goal).json()['status']=='submitted'
    reconcile(c);assert count(c)==2 and getrun(setup,rid)['status']=='running'
    assert c.post(f'/api/agent/goals/{goal}/review',headers=agent_headers(worker),json={'decision':'accept'}).status_code==403
    reviewed=c.post(f'/api/goals/{goal}/review',headers=owner,json={'decision':'accept'});assert reviewed.status_code==200,reviewed.text
    reconcile(c);assert count(c)==3
    assert finish(c,worker,goal_for(run,'t2')).json()['status']=='done';reconcile(c)
    assert getrun(setup,rid)['status']=='done'
    for g in c.app.state.hive.db.all("SELECT * FROM goals WHERE id LIKE 'g_flow_%'"):
        binding=json.loads(g['binding']);assert binding['flow_run_id']==rid
        assert binding['flow_revision_digest']==run['digest'] and g['created_by']=='user:u_flow_owner'
    assert not any(call[0]=='start' for call in c.supervisor.calls)


def test_schema_refusal_stays_with_worker_without_advancing(setup):
    c,_,_,worker,_,_,_=setup;run=adopt_start(setup)
    bad=finish(c,worker,goal_for(run,'t0'),{'ok':'wrong'})
    assert bad.status_code==422
    reconcile(c);assert count(c)==1
    assert c.app.state.hive.goals.get(goal_for(run,'t0'))['status']=='claimed'


def test_review_status_tampering_does_not_advance(setup):
    c,owner,_,worker,_,_,_=setup;run=adopt_start(setup)
    finish(c,worker,goal_for(run,'t0'));reconcile(c)
    gid=goal_for(run,'t1');finish(c,worker,gid)
    # Existing operator goal edit cannot turn a flow's unreviewed result into acceptance.
    assert c.patch('/api/goals/'+gid,headers=owner,json={'status':'claimed'}).status_code==200
    assert c.patch('/api/goals/'+gid,headers=owner,json={'status':'done'}).status_code==200
    reconcile(c);out=getrun(setup,run['id'])
    assert out['status']=='blocked' and out['reason']=='completion_unreviewed' and count(c)==2


def test_repeat_start_is_idempotent_and_key_conflicts_on_new_revision(setup):
    c,owner,swarm,_,f,flow,path=setup;run=adopt_start(setup)
    again=c.post(path+'/runs',headers=owner,json={'digest':flow['digest'],'client_key':'run-1'}).json()
    assert again['id']==run['id'] and count(c)==1
    changed=copy.deepcopy(f);changed['elements'][0]['props']['label']='other'
    nextflow=c.post(f"/api/swarms/{swarm['id']}/flows",headers=owner,json={'body':changed,'layout':{},'artifact_id':flow['artifact_id'],'parent':1}).json()
    p=f"/api/flows/{flow['artifact_id']}/revisions/2"
    assert c.post(p+'/adopt',headers=owner,json={'digest':nextflow['digest']}).status_code==200
    assert c.post(p+'/runs',headers=owner,json={'digest':nextflow['digest'],'client_key':'run-1'}).status_code==409


@pytest.mark.parametrize('stage',['after-goal-insert','before-commit','after-commit'])
def test_crash_and_fresh_controller_recovery_do_not_duplicate_goals(setup,stage):
    c,owner,_,_,_,flow,path=setup;hive=c.app.state.hive
    c.post(path+'/adopt',headers=owner,json={'digest':flow['digest']})
    session=hive.db.one("SELECT * FROM sessions WHERE principal='user:u_flow_owner'")
    run=hive.flows.start(session,flow['artifact_id'],1,{'digest':flow['digest'],'client_key':'crash-'+stage})
    class Crash(BaseException):pass
    def fault(point):
        if point==stage:raise Crash()
    hive.flows._fault=fault
    with pytest.raises(Crash):reconcile(c)
    assert count(c)==(1 if stage=='after-commit' else 0)
    fresh=Hive(hive.settings,supervisor=FakeSupervisor())
    try:
        asyncio.run(fresh.flows.reconcile());asyncio.run(fresh.flows.reconcile())
        assert count(c)==1
        assert fresh.flows.get(session,run['id'])['steps'][0]['goal_id']==goal_for(run,'t0')
    finally:fresh.db._conn.close();hive.flows._fault=lambda _:None


def test_two_controller_process_connections_admit_one_goal(setup):
    c,owner,_,_,_,flow,path=setup;hive=c.app.state.hive
    c.post(path+'/adopt',headers=owner,json={'digest':flow['digest']})
    session=hive.db.one("SELECT * FROM sessions WHERE principal='user:u_flow_owner'")
    run=hive.flows.start(session,flow['artifact_id'],1,{'digest':flow['digest'],'client_key':'race'})
    fresh=Hive(hive.settings,supervisor=FakeSupervisor())
    try:
        with ThreadPoolExecutor(2) as pool:
            futures=[pool.submit(controller._advance,run['id']) for controller in (hive.flows,fresh.flows)]
            for future in futures:future.result(timeout=10)
        assert count(c)==1
    finally:fresh.db._conn.close()


@pytest.mark.parametrize('revoke',['session','person','ownership','adoption'])
def test_revocation_blocks_run_and_cancels_outstanding_goals(setup,revoke):
    c,owner,swarm,worker,_,flow,path=setup;run=adopt_start(setup);hive=c.app.state.hive
    if revoke=='session':hive.db.execute("DELETE FROM sessions WHERE principal='user:u_flow_owner'")
    if revoke=='person':hive.db.execute("UPDATE people SET disabled=1 WHERE id='u_flow_owner'")
    if revoke=='ownership':hive.db.update('swarms',swarm['id'],{'owner':'user:u_different'})
    if revoke=='adoption':assert c.delete(path+'/adoption',headers=owner).status_code==200
    reconcile(c)
    row=hive.db.one('SELECT * FROM flow_runs WHERE id=?',(run['id'],))
    assert row['status']=='blocked' and count(c)==1
    assert hive.goals.get(goal_for(run,'t0'))['status']=='cancelled'


def test_cancellation_before_dispatch_and_after_dispatch(setup):
    c,owner,_,worker,_,flow,path=setup;hive=c.app.state.hive
    c.post(path+'/adopt',headers=owner,json={'digest':flow['digest']})
    session=hive.db.one("SELECT * FROM sessions WHERE principal='user:u_flow_owner'")
    pending=hive.flows.start(session,flow['artifact_id'],1,{'digest':flow['digest'],'client_key':'pending'})
    assert c.post('/api/flow-runs/'+pending['id']+'/cancel',headers=owner).json()['status']=='cancelled'
    reconcile(c);assert count(c)==0
    run=adopt_start(setup,'dispatched');gid=goal_for(run,'t0')
    c.post(f'/api/agent/goals/{gid}/claim',headers=agent_headers(worker))
    assert c.post('/api/flow-runs/'+run['id']+'/cancel',headers=owner).json()['status']=='cancelled'
    reconcile(c);assert count(c)==1 and hive.goals.get(gid)['status']=='cancelled'
    assert c.post(f'/api/agent/goals/{gid}/result',headers=agent_headers(worker),json={'status':'done','result':'late'}).status_code==409


@pytest.mark.parametrize('case',['cycle','guard','external-target','message','unknown-param','draft','trigger','source'])
def test_unsupported_forms_are_refused_before_run_or_goal_creation(setup,case):
    c,owner,swarm,_,f,_,_=setup;f=copy.deepcopy(f);es={e['id']:e for e in f['elements']}
    if case=='cycle':es['t2']['to']='visitor'
    if case=='guard':
        item=copy.deepcopy(es['visitor']);item.update(id='guard',kind='constraint',predicate='all-present',members=['visitor']);del item['type'];del item['ref'];f['elements'].append(item);es['t0']['guards']=['guard']
    if case=='external-target':es['t0']['action']['target']='external'
    if case=='message':es['t0']['action']['kind']='message'
    if case=='unknown-param':es['t0']['action']['params']['binding']={'authority':'admin'}
    if case=='draft':es['t0']['meta']['revision_state']='draft'
    if case=='trigger':es['submitted']['type']='external.event'
    if case=='source':es['accepted']['props']['source_transition']='unknown'
    out=c.post(f"/api/swarms/{swarm['id']}/flows",headers=owner,json={'title':'Unsupported','body':f,'layout':{}}).json()
    path=f"/api/flows/{out['artifact_id']}/revisions/1"
    assert c.post(path+'/adopt',headers=owner,json={'digest':out['digest']}).status_code in (400,409)
    assert count(c)==0 and c.app.state.hive.db.one('SELECT COUNT(*) AS n FROM flow_runs')['n']==0


def test_split_work_cancels_with_run_and_cannot_delegate_outside_subset(setup):
    c,owner,_,worker,_,_,_=setup;run=adopt_start(setup);gid=goal_for(run,'t0');auth=agent_headers(worker)
    assert c.post(f'/api/agent/goals/{gid}/claim',headers=auth).status_code==200
    child=c.post('/api/agent/goals',headers=auth,json={'title':'Synthetic child','parent_id':gid}).json()
    assert child['id'] and c.post(f"/api/agent/goals/{child['id']}/claim",headers=auth).status_code==200
    receiving=c.post('/api/swarms',json={'name':'Synthetic receiving'}).json()
    c.put(f"/api/swarms/{receiving['id']}/services",json={'kinds':['design']})
    request=c.post('/api/agent/requests',headers=auth,json={'kind':'design','to_swarm':receiving['id'],'title':'must refuse','from_goal':child['id']})
    assert request.status_code==409 and request.json()['error']['code']=='unsupported_flow_delegation'
    assert c.post('/api/flow-runs/'+run['id']+'/cancel',headers=owner).status_code==200
    assert c.app.state.hive.goals.get(child['id'])['status']=='cancelled'
    late=c.post('/api/agent/goals',headers=auth,json={'title':'late child','parent_id':gid})
    assert late.status_code==409 and late.json()['error']['code']=='parent_inactive'


def test_parent_completion_with_unfinished_child_does_not_advance(setup):
    c,_,_,worker,_,_,_=setup;run=adopt_start(setup);gid=goal_for(run,'t0');auth=agent_headers(worker)
    assert c.post(f'/api/agent/goals/{gid}/claim',headers=auth).status_code==200
    child=c.post('/api/agent/goals',headers=auth,json={'title':'Unfinished child','parent_id':gid}).json()
    g=c.get(f'/api/agent/goals/{gid}',headers=auth).json()
    assert c.post(f'/api/agent/goals/{gid}/result',headers=auth,json={'status':'done','result':'premature','data':{'binding_digest':g['binding_digest'],'proposal':{'ok':True}}}).status_code==200
    reconcile(c);out=getrun(setup,run['id'])
    assert out['status']=='blocked' and out['reason']=='delegated_work_incomplete' and count(c)==1
    assert c.app.state.hive.goals.get(child['id'])['status']=='cancelled'
