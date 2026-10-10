"""Run only against the separate host candidate named in the handoff."""
import os as _os
import pytest as _pytest
pytestmark = _pytest.mark.skipif(_os.environ.get('OMEGAALIGNMENT_HOST_CANDIDATE') != '1',
    reason='needs the superseded connection-only host candidate (host-candidate/connection-only.patch applied to its base commit); test_integrated_connection_gate.py covers the merged host; set OMEGAALIGNMENT_HOST_CANDIDATE=1 when running against it')
import pytest
from hive.tests.test_core_api import agent_headers, client  # noqa: F401
from hive.core.collab import Collab


def setup(client, private=True):
    A, B = [client.post('/api/swarms', json={'name': n}).json() for n in ('Synthetic requester', 'Synthetic alignment')]
    response = client.post('/api/roles', json={'name': 'Synthetic drift', 'prompt': 'Synthetic role only', 'mandate': {'id': 'alignment-drift', 'version': '1'}})
    assert response.status_code == 200, response.text
    role = response.json()
    a = client.post('/api/agents', json={'name': 'Synthetic asker', 'kind': 'module', 'swarm_id': A['id']}).json()
    b = client.post('/api/agents', json={'name': 'Synthetic assessor', 'kind': 'module', 'swarm_id': B['id'], 'role_id': role['id']}).json()
    service = {'kinds': ['review'], 'connection_only': ['review'] if private else []}
    r = client.put(f"/api/swarms/{B['id']}/services", json=service)
    assert r.status_code == 200, r.text
    goal = client.post(f"/api/swarms/{A['id']}/goals", json={'title': 'Synthetic review', 'assignee': a['name']}).json()
    claim = client.post(f"/api/agent/goals/{goal['id']}/claim", headers=agent_headers(a))
    assert claim.status_code == 200
    payload = {'kind': 'review', 'to_swarm': B['id'], 'title': 'Synthetic assessment', 'from_goal': goal['id'],
               'budget_usd': 0, 'constraints': {'mandates': [{'id': 'alignment-drift', 'version': '1'}]}}
    agreement = {'from_swarm': A['id'], 'to_swarm': B['id'], 'from_coordinator': a['id'], 'to_coordinator': b['id'],
                 'purpose': 'Synthetic bounded assessment', 'deliverable': 'Advisory receipt', 'days': 1, 'budget_usd': 1,
                 'scopes': [{'kind': 'requests', 'direction': 'from->to', 'kinds': ['review']}]}
    return A, B, a, b, payload, agreement


def ask(client, a, payload):
    return client.post('/api/agent/requests', headers=agent_headers(a), json=payload)


def test_advertised_private_service_needs_connection_and_readback_preserves_mode(client):
    _, B, a, _, payload, _ = setup(client)
    r = ask(client, a, payload)
    assert r.status_code == 403 and r.json()['error']['code'] == 'connection_required'
    assert client.get(f"/api/swarms/{B['id']}/services").json()['connection_only'] == ['review']
    config = client.get(f"/api/swarms/{B['id']}/services").json()
    assert config['set_by'] and config['updated_at']
    assert client.get(f"/api/swarms/{B['id']}").json()['connection_only'] == ['review']
    assert client.get(f"/api/agent/services/{B['id']}", headers=agent_headers(a)).json()['connection_only'] == ['review']
    hive = client.app.state.hive
    assert hive.db.one('SELECT COUNT(*) AS n FROM requests')['n'] == 0
    assert not any(c[0] == 'start' for c in client.supervisor.calls)


def test_public_service_remains_compatible(client):
    _, _, a, _, payload, _ = setup(client, private=False)
    r = ask(client, a, payload)
    assert r.status_code == 200 and r.json()['connection_id'] is None


def test_private_request_records_connection_and_budget(client):
    _, _, a, _, payload, agreement = setup(client)
    connection = client.post('/api/connections', json=agreement)
    assert connection.status_code == 200, connection.text
    payload['budget_usd'] = 0.4
    r = ask(client, a, payload)
    assert r.status_code == 200, r.text
    assert r.json()['connection_id'] == connection.json()['id']
    stored = client.get('/api/connections/' + connection.json()['id']).json()
    assert stored['allocated_usd'] == 0.4
    assert ask(client, a, {**payload, 'budget_usd': 0.7}).status_code == 402


@pytest.mark.parametrize('case', ['expired', 'review-due', 'paused', 'revoked', 'reverse', 'wrong-kind'])
def test_invalid_agreement_cannot_bypass_private_advertisement(client, case):
    _, _, a, _, payload, agreement = setup(client)
    if case == 'reverse': agreement['scopes'][0]['direction'] = 'to->from'
    if case == 'wrong-kind': agreement['scopes'][0]['kinds'] = ['plan']
    r = client.post('/api/connections', json=agreement)
    assert r.status_code == 200, r.text
    hive = client.app.state.hive
    if case in {'expired', 'review-due'}:
        hive.db.update('connections', r.json()['id'], {'ends_at' if case == 'expired' else 'review_at': '2000-01-01T00:00:00.000Z'})
    if case in {'paused', 'revoked'}:
        hive.db.update('connections', r.json()['id'], {'status': case})
    denied = ask(client, a, payload)
    assert denied.status_code == 403, denied.text
    assert hive.db.one('SELECT COUNT(*) AS n FROM requests')['n'] == 0


def test_legacy_update_cannot_silently_erase_private_gate(client):
    _, B, a, _, payload, _ = setup(client)
    r = client.put(f"/api/swarms/{B['id']}/services", json={'kinds': ['review']})
    assert r.status_code == 200 and r.json()['connection_only'] == ['review']
    assert ask(client, a, payload).status_code == 403
    hive = client.app.state.hive
    Collab(hive)
    assert hive.collab.service_config(B['id'])['connection_only'] == ['review']


@pytest.mark.parametrize('private', [None, 'review', [True], ['unknown'], [None]])
def test_bad_modes_refuse_without_resetting_private_gate(client, private):
    _, B, _, _, _, _ = setup(client)
    r = client.put(f"/api/swarms/{B['id']}/services", json={'kinds': ['review'], 'connection_only': private})
    assert r.status_code == 400, r.text
    assert client.get(f"/api/swarms/{B['id']}/services").json()['connection_only'] == ['review']


def test_agent_cannot_change_service_mode(client):
    _, B, a, _, _, _ = setup(client)
    r = client.put(f"/api/swarms/{B['id']}/services", headers=agent_headers(a), json={'kinds': ['review'], 'connection_only': []})
    assert r.status_code in {401, 403}
    assert client.get(f"/api/swarms/{B['id']}/services").json()['connection_only'] == ['review']


def test_removing_private_kind_requires_explicit_gate_clear(client):
    _, B, _, _, _, _ = setup(client)
    r = client.put(f"/api/swarms/{B['id']}/services", json={'kinds': []})
    assert r.status_code == 400
    assert client.get(f"/api/swarms/{B['id']}/services").json()['connection_only'] == ['review']
    r = client.put(f"/api/swarms/{B['id']}/services", json={'kinds': [], 'connection_only': []})
    assert r.status_code == 200 and r.json()['connection_only'] == []


def test_legacy_service_schema_migrates_as_public(client):
    hive = client.app.state.hive
    swarm = client.post('/api/swarms', json={'name': 'Synthetic legacy service'}).json()
    hive.db.execute('ALTER TABLE swarm_services DROP COLUMN connection_only')
    hive.db.execute('INSERT INTO swarm_services VALUES (?, ?, ?, ?)',
                    (swarm['id'], '["plan"]', 'synthetic-admin', '2026-10-04T00:00:00.000Z'))
    Collab(hive)
    config = hive.collab.service_config(swarm['id'])
    assert config['kinds'] == ['plan'] and config['connection_only'] == []
    assert config['set_by'] == 'synthetic-admin'
