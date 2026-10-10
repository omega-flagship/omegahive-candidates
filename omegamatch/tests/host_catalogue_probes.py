"""Explicit disposable probes for the partial requester-scoped catalogue candidate."""
from pathlib import Path
import pytest
from hive.tests.test_core_api import client, agent_headers
from omegamatch.tests.host_transport_probes import setup, submit


@pytest.fixture(autouse=True)
def mount_program(monkeypatch):
    monkeypatch.setenv('HIVE_PLUGIN_DIRS', str(Path(__file__).resolve().parents[1] / 'program'))


def test_actual_host_projection_refuses_without_semantic_witnesses(client, monkeypatch):
    asker, mind, request, bound, inputs, output = setup(client, validate='program:omegamatch')
    hive = client.app.state.hive
    entry = hive.programs._ready('omegamatch')
    original = entry['module'].validate_result
    inspected = []

    def inspect_context(ctx, goal, proposal):
        assert ctx.validation['requester_swarm'] == request['from_swarm']
        assert ctx.viewer_for_requester.admin is False
        with pytest.raises(Exception):
            ctx.catalogue(request['to_swarm'])
        projection = ctx.catalogue(request['from_swarm'])
        assert projection['requester_swarm'] == request['from_swarm']
        assert projection['truncated'] is True
        assert all(o['tier'] == 'advertised' for o in projection['offers'])
        inspected.append(projection['catalogue_digest'])
        return original(ctx, goal, proposal)

    monkeypatch.setattr(entry['module'], 'validate_result', inspect_context)
    response = submit(client, mind, bound, output)
    assert response.status_code == 422, response.text
    assert 'match_semantic_context_unavailable' in response.text
    assert len(inspected) == 1
    state = client.get(f"/api/agent/goals/{bound['id']}", headers=agent_headers(mind)).json()
    assert state['status'] == 'claimed' and not state.get('result_data')
    attempts = client.get(f"/api/goals/{bound['id']}/attempts").json()
    assert any(not attempt['ok'] and 'match_semantic_context_unavailable' in str(attempt['errors']) for attempt in attempts)
    assert not any(call[0] == 'start' for call in client.supervisor.calls)
