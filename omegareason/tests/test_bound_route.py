"""L1: real disposable ASGI host/PeTTa, fake supervisor, no live runtime."""
import copy,json,os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from hive.core.app import create_app
from hive.core.config import load_settings
from hive.tests.test_core_api import FakeSupervisor,agent_headers
from omegaatom.envelope import digest,dumps,validate
from omegareason.qualify_bridge import source
from omegareason.bound_worker import prepare,finalize,Refused
ROOT=Path(__file__).resolve().parents[2]

PROGRAM='''
import json
from pathlib import Path
from omegaatom.envelope import validate,digest
STATE=Path(__file__).with_name('snapshot.json')
def current():return validate(json.loads(STATE.read_text()))
def describe():return {'contract':'0.1','kinds':[{'id':'claim','label':'Claim','role':'claim'}],'relations':[],'actions':[{'id':'ask','label':'Ask','applies_to':['claim']}]}
def view(ctx,focus,stage):return {'revision':str(current()['revision']),'items':[{'id':'question','kind':'claim','label':'Question'}]}
async def act(ctx,action,items,params):
    s=current()
    out=await ctx.bound_request('Reason over snapshot','Reason',{'title':'Frozen Atom snapshot','body':json.dumps(s),'atoms':[]},
        {'request_id':params['request_id'],'base_revision':s['revision'],'envelope_digest':digest(s),'validate':'program:reason-fixture'},deadline_minutes=5)
    return {'status':'started','task':{'id':out['goal']['id'],'kind':'goal','status':'open'},'detail':{'binding':out['binding']}}
def validate_result(ctx,goal,proposal):
    if digest(current())!=goal['binding']['envelope_digest']:return {'errors':['owner snapshot changed']}
    try:validate(proposal['snapshot'])
    except Exception as e:return {'errors':[str(e)]}
    return {'ok':True}
'''

@pytest.fixture
def rig(tmp_path,monkeypatch):
    folder=tmp_path/'program';folder.mkdir()
    (folder/'plugin.json').write_text(json.dumps({'id':'reason-fixture','name':'Reason fixture','capabilities':['goals:read','goals:write','exhibits:write']}))
    (folder/'program.py').write_text(PROGRAM)
    base={'version':'0.1','owner':'lab','scope':'synthetic-atom','revision':1,'records':[
        source(1,['Inheritance','alpha','beta'],['stv',.8,.7]),source(2,['Inheritance','beta','gamma'],['stv',.8,.7]),
        *[source(i+3,['TermCounts',t,50,100],['stv',.5,100/101]) for i,t in enumerate(['alpha','beta','gamma'])]]}
    (folder/'snapshot.json').write_text(dumps(base))
    monkeypatch.setenv('HIVE_PLUGIN_DIRS',str(folder))
    supervisor=FakeSupervisor()
    settings=load_settings(data_dir=tmp_path/'host',admin_password='synthetic',petta_path=os.environ.get('PETTA_PATH') or str(ROOT/'.runtime/PeTTa'))
    app=create_app(settings,supervisor=supervisor,reconcile_seconds=0)
    with TestClient(app) as c:
        token=c.post('/api/auth/login',json={'password':'synthetic'}).json()['token']
        c.headers['Authorization']='Bearer '+token
        swarm=c.post('/api/swarms',json={'name':'Synthetic Reason Lab'}).json()
        agent=c.post('/api/agents',json={'name':'Reason','kind':'module','swarm_id':swarm['id']}).json()
        other=c.post('/api/agents',json={'name':'Other','kind':'module','swarm_id':swarm['id']}).json()
        yield c,swarm,agent,other,base,folder,supervisor

def call(c,a,method,path,body=None):return c.request(method,path,headers=agent_headers(a),json=body)
def request(rig):
    c,s,a,o,base,folder,supervisor=rig
    result=c.post('/api/programs/reason-fixture/act',json={'swarm_id':s['id'],'action':'ask','items':['question'],'params':{'request_id':'synthetic-request'}})
    assert result.status_code==200,result.text
    gid=result.json()['task']['id']
    assert call(c,o,'POST',f'/api/agent/goals/{gid}/claim').status_code==403
    claimed=call(c,a,'POST',f'/api/agent/goals/{gid}/claim');assert claimed.status_code==200,claimed.text
    goal=call(c,a,'GET',f'/api/agent/goals/{gid}').json()
    exhibit=call(c,a,'GET',f"/api/agent/shares/{goal['binding']['share_ids'][0]}/atoms").json()
    return gid,goal,exhibit

def test_real_bound_reasoning_result_and_retry(rig):
    c,s,a,o,base,folder,supervisor=rig;gid,goal,ex=request(rig)
    prepared=prepare(goal,ex,a['id'])
    proposal=prepared['data']['proposal']['snapshot']
    assert any(r['statement']==['Inheritance','alpha','gamma'] for r in proposal['records'])
    assert any(r['statement'][0]=='Restriction' and r['unknown'] for r in proposal['records'])
    fresh=call(c,a,'GET',f'/api/agent/goals/{gid}').json()
    assert call(c,a,'POST',f'/api/agent/goals/{gid}/heartbeat').status_code==200
    payload=finalize(prepared,fresh,base)
    response=call(c,a,'POST',f'/api/agent/goals/{gid}/result',payload)
    assert response.status_code==200,response.text
    assert call(c,a,'POST',f'/api/agent/goals/{gid}/result',payload).status_code==200
    changed=copy.deepcopy(payload);changed['result']='different result'
    assert call(c,a,'POST',f'/api/agent/goals/{gid}/result',changed).status_code==409
    assert not any(x[0]=='start' for x in supervisor.calls)
    assert not c.get('/api/usage').json()

def test_cancellation_revocation_late_result_and_ack(rig):
    c,s,a,o,base,folder,supervisor=rig;gid,goal,ex=request(rig)
    prepared=prepare(goal,ex,a['id']);payload=finalize(prepared,goal,base)
    assert c.patch('/api/goals/'+gid,json={'status':'cancelled'}).status_code==200
    fresh=call(c,a,'GET',f'/api/agent/goals/{gid}').json()
    with pytest.raises(Refused):finalize(prepared,fresh,base)
    assert call(c,a,'GET',f"/api/agent/shares/{goal['binding']['share_ids'][0]}/atoms").status_code==410
    assert call(c,a,'POST',f'/api/agent/goals/{gid}/result',payload).status_code==409
    assert call(c,a,'POST',f'/api/agent/goals/{gid}/cancel-ack').status_code==200

def test_snapshot_correction_refuses_worker_and_host_result(rig):
    c,s,a,o,base,folder,supervisor=rig;gid,goal,ex=request(rig)
    prepared=prepare(goal,ex,a['id']);payload=finalize(prepared,goal,base)
    changed=copy.deepcopy(base);changed['revision']=2
    (folder/'snapshot.json').write_text(dumps(changed))
    with pytest.raises(Refused):finalize(prepared,goal,changed)
    refused=call(c,a,'POST',f'/api/agent/goals/{gid}/result',payload)
    assert refused.status_code==422,refused.text

def test_forged_or_partial_exhibit_refused(rig):
    c,s,a,o,base,folder,supervisor=rig;gid,goal,ex=request(rig)
    for key,value in [('body','{}'),('complete',False),('share_id','unbound'),('offset',1)]:
        wrong=copy.deepcopy(ex);wrong[key]=value
        with pytest.raises(Refused):prepare(goal,wrong,a['id'])
    with pytest.raises(Refused):prepare(goal,ex,o['id'])

def test_deadline_and_lease_expiry_refuse_submission(rig):
    c,s,a,o,base,folder,supervisor=rig;gid,goal,ex=request(rig)
    prepared=prepare(goal,ex,a['id']);payload=finalize(prepared,goal,base)
    for key in ['deadline_at','lease_until']:
        expired=copy.deepcopy(goal);expired[key]='2000-01-01T00:00:00Z'
        with pytest.raises(Refused):finalize(prepared,expired,base)
    c.app.state.hive.db.execute('UPDATE goals SET deadline_at = ? WHERE id = ?',('2000-01-01T00:00:00Z',gid))
    assert call(c,a,'POST',f'/api/agent/goals/{gid}/result',payload).status_code==409
    # Expiry notification/ack is the host reconciler's job; the test disables its timer.
    assert gid in c.portal.call(c.app.state.hive.goals.expire)
    assert call(c,a,'POST',f'/api/agent/goals/{gid}/cancel-ack').status_code==200

def test_executable_snapshot_refused_even_with_consistent_transport_digest(rig):
    from hive.core.goals import binding_digest
    from hive.core.shares import exhibit_digest
    c,s,a,o,base,folder,supervisor=rig;gid,goal,ex=request(rig)
    bad=copy.deepcopy(base);bad['records'][0]['statement']=['import!','dangerous-module']
    exhibit=copy.deepcopy(ex);exhibit['body']=json.dumps(bad)
    exhibit['digest']=exhibit_digest(exhibit['title'],exhibit['body'],exhibit['atoms'])
    forged=copy.deepcopy(goal);forged['binding']['snapshot_digest']=exhibit['digest']
    forged['binding']['envelope_digest']=digest(bad)
    forged['binding_digest']=binding_digest(forged['binding'])
    with pytest.raises(ValueError,match='executable'):prepare(forged,exhibit,a['id'])
