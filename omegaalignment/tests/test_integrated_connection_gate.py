"""Run only against the separate host candidate named in the handoff."""
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
    service = {'kinds': [] if private else ['review'], 'connection_only_kinds': ['review'] if private else []}
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
    if case == 'review-due':
        agreement['until_revoked'] = True
        agreement['review_days'] = 1
        agreement.pop('days', None)
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


def test_omission_preserves_connection_scope(client):
    _, B, a, _, payload, _ = setup(client)
    r = client.put(f"/api/swarms/{B['id']}/services", json={'kinds': []})
    assert r.status_code == 200
    assert r.json()['connection_only_kinds'] == ['review']
    assert ask(client, a, payload).status_code == 403


def test_overlap_cannot_make_private_service_public(client):
    _, B, _, _, _, _ = setup(client)
    r = client.put(f"/api/swarms/{B['id']}/services", json={'kinds': ['review']})
    assert r.status_code == 400
    assert client.get(f"/api/swarms/{B['id']}/services").json()['connection_only_kinds'] == ['review']


def test_explicit_clear(client):
    _, B, _, _, _, _ = setup(client)
    r = client.put(f"/api/swarms/{B['id']}/services", json={'kinds': [], 'connection_only_kinds': []})
    assert r.status_code == 200 and r.json()['connection_only_kinds'] == []
