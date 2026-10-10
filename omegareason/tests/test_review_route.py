"""L1 two actual synthetic swarms; retained artifacts and real review completion."""
import copy
import pytest
from omegaatom.envelope import digest
from omegareason.atom_bridge import infer_snapshot
from omegareason.review_export import seal,open_revision,review_request
from .test_bound_route import rig,call

@pytest.fixture
def reviewing(rig):
    c,s,a,o,base,folder,supervisor=rig
    swarm=c.post('/api/swarms',json={'name':'Independent synthetic Review'}).json()
    role=c.post('/api/roles',json={'name':'Synthetic lineage reviewer','prompt':'Review synthetic provenance only',
           'mandate':{'id':'reason-lineage','version':'1'}}).json()
    reviewer=c.post('/api/agents',json={'name':'Reviewer','kind':'module','swarm_id':swarm['id'],'role_id':role['id']}).json()
    assert c.put('/api/swarms/'+swarm['id']+'/services',json={'kinds':['review']}).status_code==200
    root=c.post('/api/swarms/'+s['id']+'/goals',json={'title':'Synthetic Reason investigation','assignee':a['id']}).json()
    assert call(c,a,'POST',f"/api/agent/goals/{root['id']}/claim").status_code==200
    body=seal(infer_snapshot(base)['snapshot'])
    artifact=call(c,a,'POST','/api/agent/artifacts',{'kind':'reasoning-proposal','title':'Synthetic reasoning evidence'}).json()
    path=f"/api/agent/artifacts/{artifact['id']}/revisions"
    first=call(c,a,'POST',path,{'body':body,'parent':None}).json()
    second_snapshot=copy.deepcopy(base);second_snapshot['revision']=2
    second=call(c,a,'POST',path,{'body':seal(second_snapshot),'parent':1}).json()
    subject={'artifact_id':artifact['id'],'revision':first['n'],'digest':first['digest']}
    assert call(c,reviewer,'GET',path+'/1').status_code==403
    requested=call(c,a,'POST','/api/agent/requests',review_request(root['id'],swarm['id'],subject))
    assert requested.status_code==200,requested.text
    yield rig,reviewer,path,first,second,subject,requested.json()

def test_retained_revision_real_review_completion_closes_access(reviewing):
    rig,reviewer,path,first,second,subject,request=reviewing
    c,s,a,o,base,folder,supervisor=rig
    read=call(c,reviewer,'GET',path+'/1');assert read.status_code==200,read.text
    report=open_revision(read.json(),subject)
    assert report['authority']=='proposal-only'
    assert any(r['status']=='inferred' for r in report['snapshot']['records'])
    assert call(c,reviewer,'GET',path+'/2').status_code==403
    assert call(c,reviewer,'POST',f"/api/agent/goals/{request['receiving_goal']}/claim").status_code==200
    complete=call(c,reviewer,'POST',f"/api/agent/requests/{request['id']}/review-complete",{
        'recommendation':'unresolved','rationale':'Synthetic route test; no scientific acceptance or adoption',
        'finding_ids':[],'coverage':['lineage']})
    assert complete.status_code==200,complete.text
    assert complete.json()['receipt']['authority']=='none' and complete.json()['receipt']['recommendation']=='unresolved'
    assert call(c,reviewer,'GET',path+'/1').status_code==403
    assert not any(x[0]=='start' for x in supervisor.calls)
    assert not c.get('/api/usage').json()

def test_cancelled_request_closes_review_read_and_result(reviewing):
    rig,reviewer,path,first,second,subject,request=reviewing
    c,s,a,o,base,folder,supervisor=rig
    assert call(c,reviewer,'POST',f"/api/agent/goals/{request['receiving_goal']}/claim").status_code==200
    cancelled=call(c,a,'POST',f"/api/agent/requests/{request['id']}/cancel")
    assert cancelled.status_code==200,cancelled.text
    assert call(c,reviewer,'GET',path+'/1').status_code==403
    late=call(c,reviewer,'POST',f"/api/agent/requests/{request['id']}/review-complete",{
        'recommendation':'proceed','rationale':'Too late','finding_ids':[],'coverage':[]})
    assert late.status_code==403 and late.json()['error']['code']=='review_not_held',late.text
    assert call(c,reviewer,'POST',f"/api/agent/goals/{request['receiving_goal']}/cancel-ack").status_code==200

def test_export_tampering_and_wrong_revision_are_refused(reviewing):
    rig,reviewer,path,first,second,subject,request=reviewing
    c,s,a,o,base,folder,supervisor=rig
    read=call(c,reviewer,'GET',path+'/1').json()
    tampered=copy.deepcopy(read);tampered['body']+=' '
    with pytest.raises(ValueError,match='digest'):open_revision(tampered,subject)
    wrong=copy.deepcopy(subject);wrong['revision']=2
    with pytest.raises(ValueError,match='revision'):open_revision(read,wrong)
