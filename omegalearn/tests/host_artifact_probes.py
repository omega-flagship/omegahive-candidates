"""L1 disposable real host/PeTTa with fake supervisor; no live listener."""
import os
import pathlib
import pytest
from fastapi.testclient import TestClient
from hive.core.app import create_app
from hive.core.config import load_settings
from hive.core.programs import ProgramContext
from hive.tests.test_core_api import FakeSupervisor,make_swarm_and_agents
from omegalearn.adapters import publish_candidate
from omegalearn.tests.test_foundation import setup

@pytest.fixture
def client(tmp_path):
    settings=load_settings(data_dir=tmp_path/'data',admin_password='pw',petta_path=os.environ.get('PETTA_PATH') or str(pathlib.Path('.runtime/PeTTa').resolve()))
    with TestClient(create_app(settings,supervisor=FakeSupervisor(),reconcile_seconds=0)) as c:
        c.headers['Authorization']='Bearer '+c.post('/api/auth/login',json={'password':'pw'}).json()['token']
        yield c

def context(hive,a,caps):
    c=ProgramContext(hive,a['swarm_id'],{'id':'omegalearn','capabilities':caps});c.actor={'kind':'mind','id':a['id']};return c

def test_actual_publish_readback_and_other_swarm_refusal(client):
    h=client.app.state.hive;_,(a,b)=make_swarm_and_agents(client)
    l,e,k=setup();c=context(h,a,['artifacts:write','artifacts:read']);out=publish_candidate(c,l,k)
    assert out['stage']=='published-proposal' and out['attached'] is False
    _,(x,y)=make_swarm_and_agents(client)
    foreign=context(h,x,['artifacts:read'])
    with pytest.raises(Exception):foreign.read_revision(out['artifact']['artifact_id'],out['artifact']['revision'])

def test_actor_and_capability_required(client):
    h=client.app.state.hive;_,(a,b)=make_swarm_and_agents(client);l,e,k=setup()
    c=context(h,a,[])
    with pytest.raises(Exception):publish_candidate(c,l,k)
    c=context(h,a,['artifacts:write','artifacts:read']);c.actor=None
    with pytest.raises(Exception):publish_candidate(c,l,k)

def test_retracted_candidate_cannot_publish(client):
    h=client.app.state.hive;_,(a,b)=make_swarm_and_agents(client);l,e,k=setup();l.invalidate(e['id'],lambda _:True)
    count=h.db.one('SELECT count(*) AS n FROM artifacts')['n']
    with pytest.raises(Exception):publish_candidate(context(h,a,['artifacts:write','artifacts:read']),l,k)
    assert h.db.one('SELECT count(*) AS n FROM artifacts')['n']==count

def test_source_owner_export_is_read_under_learn_actor_not_operator(client):
    from omegalearn.adapters import resolve_artifact_export
    from omegalearn.tests.test_foundation import event,resolver
    from omegalearn import Ledger
    h=client.app.state.hive;_,(source,learner)=make_swarm_and_agents(client)
    exported=context(h,source,['artifacts:write']).publish('learning-source','Synthetic error','{"error":"missing closer"}')
    e=event();e['owner']='agent:'+source['id'];e['scope']=source['swarm_id'];e['subject']={'id':exported['artifact_id'],'revision':str(exported['revision']),'digest':exported['digest'].removeprefix('sha256:')}
    readctx=context(h,learner,['artifacts:read']);trusted=resolver(e)
    assert Ledger().admit(e,lambda x:resolve_artifact_export(readctx,x,trusted))['new_evidence']
    bad=dict(trusted,current_subject=dict(e['subject'],revision='2'))
    with pytest.raises(Exception):resolve_artifact_export(readctx,e,bad)
    e['owner']='agent:'+learner['id']
    with pytest.raises(Exception):resolve_artifact_export(readctx,e,trusted)
