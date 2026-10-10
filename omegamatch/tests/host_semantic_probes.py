"""Current uncommitted generic-hook snapshot; exact patch retained separately.

No host monkeypatches or fake catalogue injected: tests exercise the actual hook
and verify Match refuses without trusted catalogue context.
"""
from pathlib import Path
import pytest
from hive.tests.test_core_api import client, agent_headers  # noqa: F401
from omegamatch.tests.host_transport_probes import setup,submit


@pytest.fixture(autouse=True)
def mount_program(monkeypatch):
    monkeypatch.setenv('HIVE_PLUGIN_DIRS',str(Path(__file__).resolve().parents[1]/'program'))


def test_match_hook_refuses_missing_catalogue_and_keeps_attempt(client):
    asker,mind,request,bound,inputs,output=setup(client,validate='program:omegamatch')
    response=submit(client,mind,bound,output)
    assert response.status_code==422,response.text
    assert 'match_host_context_unavailable' in response.text,response.text
    state=client.get(f"/api/agent/goals/{bound['id']}",headers=agent_headers(mind)).json()
    assert state['status']=='claimed' and not state.get('result_data'),state
    attempts=client.get(f"/api/goals/{bound['id']}/attempts").json()
    assert any(not a['ok'] and 'match_host_context_unavailable' in str(a['errors']) for a in attempts),attempts
    assert not any(call[0]=='start' for call in client.supervisor.calls)


def test_promoted_evidence_cannot_bypass_missing_context_hook(client):
    asker,mind,request,bound,inputs,output=setup(client,validate='program:omegamatch')
    output['evidence_refs'][0]['basis']='accepted-performance'
    response=submit(client,mind,bound,output)
    assert response.status_code==422,response.text
    assert client.get(f"/api/agent/goals/{bound['id']}",headers=agent_headers(mind)).json()['status']=='claimed'


def test_unknown_validator_refuses_completion(client):
    asker,mind,request,bound,inputs,output=setup(client,validate='program:missing-match-validator')
    response=submit(client,mind,bound,output)
    assert response.status_code==422,response.text
    assert client.get(f"/api/agent/goals/{bound['id']}",headers=agent_headers(mind)).json()['status']=='claimed'
