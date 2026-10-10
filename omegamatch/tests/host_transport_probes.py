"""Explicit disposable ASGI probes; not automatically collected by pure suite.

Use PYTHONPATH pointing at the retained host source. Fake supervisor, no server
listener, provider calls or running native minds. Evidence is invented.
"""
from copy import deepcopy
from hive.tests.test_core_api import client, agent_headers  # noqa: F401
from omegamatch.protocol import ReuseAdmission
from omegamatch.schema import reuse_alert_schema
from omegamatch.swarm import blueprint
from omegamatch.tests.test_protocol import fixture


def setup(client, validate=None):
    config=blueprint()
    requester=client.post('/api/swarms',json={'name':'Invented Requester'}).json()
    match=client.post('/api/swarms',json=config['swarm']).json()
    asker=client.post('/api/agents',json={'name':'Invented Asker','kind':'module','swarm_id':requester['id']}).json()
    role=client.post('/api/roles',json=config['roles'][1]['fields']).json()
    assert 'id' in role,role
    mind=client.post('/api/agents',json={'name':'Invented Match','kind':'module','swarm_id':match['id'],'role_id':role['id']}).json()
    assert mind['status']=='created',mind
    assert client.put(f"/api/swarms/{match['id']}/services",json={'kinds':['match']} # Explicit disposable public fixture, not production connection policy
        ).status_code==200
    parent=client.post(f"/api/swarms/{requester['id']}/goals",json={'title':'Invented reuse need'}).json()
    assert client.post(f"/api/agent/goals/{parent['id']}/claim",headers=agent_headers(asker)).status_code==200
    inputs,output=fixture()
    # Host allocates request_id during creation, so freeze the known context
    # fields now and check the allocated ID in semantic admission afterward.
    schema=reuse_alert_schema(need_id=inputs['need_id'])
    for key,value in inputs['binding'].items():
        if key != 'request_id':
            schema['properties']['binding']['properties'][key]['const']=value
    response=client.post('/api/agent/requests',headers=agent_headers(asker),json={
        'from_goal':parent['id'],'to_swarm':match['id'],'kind':'match',
        'title':'Find existing invented CSV operation','budget_usd':0,
        'constraints':{'result_schema':schema, **({'validate':validate} if validate else {})},'acceptance':['Return evidence-bound recommendation only']})
    assert response.status_code==200,response.text
    request=response.json();goal=request['receiving_goal']
    inputs['binding']['request_id']=request['id']
    output['binding']['request_id']=request['id']
    assert client.post(f'/api/agent/goals/{goal}/claim',headers=agent_headers(mind)).status_code==200
    bound=client.get(f'/api/agent/goals/{goal}',headers=agent_headers(mind)).json()
    return asker,mind,request,bound,inputs,output


def submit(client,mind,bound,proposal):
    return client.post(f"/api/agent/goals/{bound['id']}/result",headers=agent_headers(mind),json={
        'status':'done','result':'Reuse candidate returned for requester assessment',
        'data':{'binding_digest':bound['binding_digest'],'proposal':proposal}})


def test_schema_repair_and_authenticated_return_without_activation(client):
    asker,mind,request,bound,inputs,output=setup(client)
    invalid=deepcopy(output);invalid['authority']='execute'
    refused=submit(client,mind,bound,invalid)
    assert refused.status_code==422,refused.text
    assert client.get(f"/api/agent/goals/{bound['id']}",headers=agent_headers(mind)).json()['status']=='claimed'
    admitted=ReuseAdmission(**inputs).admit(output,current_binding=inputs['binding'])
    assert admitted.acceptance=='pending' and admitted.execution_authorized is False
    accepted=submit(client,mind,bound,admitted.result)
    assert accepted.status_code==200,accepted.text
    returned=client.get(f"/api/agent/requests/{request['id']}",headers=agent_headers(asker)).json()
    assert returned['result']['proposal']==output
    assert not any(call[0]=='start' for call in client.supervisor.calls)


def test_cancelled_request_refuses_late_output(client):
    asker,mind,request,bound,inputs,output=setup(client)
    cancelled=client.post(f"/api/agent/requests/{request['id']}/cancel",headers=agent_headers(asker))
    assert cancelled.status_code==200,cancelled.text
    late=submit(client,mind,bound,output)
    assert late.status_code==409,late.text
    assert not any(call[0]=='start' for call in client.supervisor.calls)


def test_foreign_mind_cannot_submit_match_result(client):
    asker,mind,request,bound,inputs,output=setup(client)
    foreign_swarm=client.post('/api/swarms',json={'name':'Invented Foreign'}).json()
    foreign=client.post('/api/agents',json={'name':'Invented Other','kind':'module','swarm_id':foreign_swarm['id']}).json()
    response=submit(client,foreign,bound,output)
    assert response.status_code==403,response.text


def test_schema_alone_does_not_enforce_evidence_semantics(client):
    # Diagnostic acceptance gap, not a security-pass claim: the host currently
    # validates shape only and does not install Match's semantic admission.
    from omegamatch.protocol import Refused
    import pytest
    asker,mind,request,bound,inputs,output=setup(client)
    output['evidence_refs'][0]['basis']='accepted-performance'
    with pytest.raises(Refused,match='evidence_unavailable_or_changed'):
        ReuseAdmission(**inputs).admit(output,current_binding=inputs['binding'])
    response=submit(client,mind,bound,output)
    assert response.status_code==200,response.text
    assert response.json()['status']=='done'
    assert not any(call[0]=='start' for call in client.supervisor.calls)
