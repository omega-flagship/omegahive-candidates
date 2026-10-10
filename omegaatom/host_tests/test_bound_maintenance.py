"""L1 real ASGI/PeTTa bound route, fake supervisor; no S1/S1b claim."""
import copy
import os
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from hive.core.app import create_app
from hive.core.config import load_settings
from hive.tests.test_core_api import FakeSupervisor, agent_headers
from omegaatom import Refused, stage_append
from omegaatom.envelope import digest, dumps
from omegaatom.e1 import fixture, control
from omegaatom.bound_worker import prepare, finalize

ROOT = Path(__file__).resolve().parents[2]
PROGRAM = '''
import json
from pathlib import Path
from omegaatom.envelope import loads,digest
from omegaatom.bound_worker import validate_result as check_result
STATE=Path(__file__).with_name('snapshot.json')
def current():return loads(STATE.read_text())
def describe():return {'contract':'0.1','kinds':[{'id':'claim','label':'Claim','role':'claim'}],'relations':[],'actions':[{'id':'ask','label':'Ask','applies_to':['claim']}]}
def view(ctx,focus,stage):return {'revision':str(current()['revision']),'items':[{'id':'maintenance','kind':'claim','label':'Maintenance request'}]}
async def act(ctx,action,items,params):
    s=current()
    out=await ctx.bound_request('Maintain frozen synthetic space','Maintainer',{'title':'Frozen Atom snapshot','body':json.dumps(s),'atoms':[]},
        {'request_id':params['request_id'],'base_revision':s['revision'],'envelope_digest':digest(s),'validate':'program:atom-maintenance-fixture'},deadline_minutes=5)
    return {'status':'started','task':{'id':out['goal']['id'],'kind':'goal','status':'open'},'detail':{'binding':out['binding']}}
def validate_result(ctx,goal,proposal):
    try:
        check_result(proposal,current())
        if digest(current())!=goal['binding']['envelope_digest']:return {'errors':['owner snapshot changed']}
    except ValueError as error:return {'errors':[str(error)]}
    return {'ok':True}
'''


@pytest.fixture
def rig(tmp_path, monkeypatch):
    folder = tmp_path / "program"
    folder.mkdir()
    (folder / "plugin.json").write_text(json.dumps({"id": "atom-maintenance-fixture", "name": "Atom maintenance fixture", "capabilities": ["goals:read", "goals:write", "exhibits:write"]}))
    (folder / "program.py").write_text(PROGRAM)
    base, ids, _ = fixture()
    withdrawn = stage_append(base, [control(["ev", "atom-control", 1], ids["failure"], 1, 10)], expected_revision=base["revision"], expected_digest=digest(base))["snapshot"]
    (folder / "snapshot.json").write_text(dumps(withdrawn))
    monkeypatch.setenv("HIVE_PLUGIN_DIRS", str(folder))
    supervisor = FakeSupervisor()
    settings = load_settings(data_dir=tmp_path / "host", admin_password="synthetic", petta_path=os.environ.get("PETTA_PATH") or str(ROOT / ".runtime/PeTTa"))
    app = create_app(settings, supervisor=supervisor, reconcile_seconds=0)
    with TestClient(app) as client:
        token = client.post("/api/auth/login", json={"password": "synthetic"}).json()["token"]
        client.headers["Authorization"] = "Bearer " + token
        swarm = client.post("/api/swarms", json={"name": "Synthetic Atom Lab"}).json()
        maintainer = client.post("/api/agents", json={"name": "Maintainer", "kind": "module", "swarm_id": swarm["id"]}).json()
        other = client.post("/api/agents", json={"name": "Other", "kind": "module", "swarm_id": swarm["id"]}).json()
        yield client, swarm, maintainer, other, withdrawn, folder, supervisor


def call(client, agent, method, path, body=None):
    return client.request(method, path, headers=agent_headers(agent), json=body)


def request(rig):
    c, swarm, agent, other, _, _, _ = rig
    response = c.post("/api/programs/atom-maintenance-fixture/act", json={"swarm_id": swarm["id"], "action": "ask", "items": ["maintenance"], "params": {"request_id": "synthetic-maintenance"}})
    assert response.status_code == 200, response.text
    gid = response.json()["task"]["id"]
    assert call(c, other, "POST", f"/api/agent/goals/{gid}/claim").status_code == 403
    assert call(c, agent, "POST", f"/api/agent/goals/{gid}/claim").status_code == 200
    goal = call(c, agent, "GET", f"/api/agent/goals/{gid}").json()
    share = goal["binding"]["share_ids"][0]
    exhibit = call(c, agent, "GET", f"/api/agent/shares/{share}/atoms").json()
    return gid, goal, exhibit


def test_real_host_binds_maintenance_and_identical_retry(rig):
    c, _, agent, _, base, _, supervisor = rig
    gid, goal, exhibit = request(rig)
    prepared = prepare(goal, exhibit, agent["id"], now=20)
    assert len(prepared["proposal"]["proposals"]) == 5
    assert all(p["action"] == "mark-stale" and p["authority"] == "none" for p in prepared["proposal"]["proposals"])
    assert call(c, agent, "POST", f"/api/agent/goals/{gid}/heartbeat").status_code == 200
    fresh = call(c, agent, "GET", f"/api/agent/goals/{gid}").json()
    payload = finalize(prepared, fresh, base)
    response = call(c, agent, "POST", f"/api/agent/goals/{gid}/result", payload)
    assert response.status_code == 200, response.text
    assert call(c, agent, "POST", f"/api/agent/goals/{gid}/result", payload).status_code == 200
    changed = copy.deepcopy(payload)
    changed["result"] = "changed payload"
    assert call(c, agent, "POST", f"/api/agent/goals/{gid}/result", changed).status_code == 409
    assert not any(item[0] == "start" for item in supervisor.calls)
    assert c.get("/api/usage").json() == []


def test_current_snapshot_change_refused_by_worker_and_host(rig):
    c, _, agent, _, base, folder, _ = rig
    gid, goal, exhibit = request(rig)
    prepared = prepare(goal, exhibit, agent["id"], now=20)
    payload = finalize(prepared, goal, base)
    changed = copy.deepcopy(base)
    changed["revision"] += 1
    (folder / "snapshot.json").write_text(dumps(changed))
    with pytest.raises(Refused, match="stale"):
        finalize(prepared, goal, changed)
    response = call(c, agent, "POST", f"/api/agent/goals/{gid}/result", payload)
    assert response.status_code == 422, response.text


def test_cancel_revokes_exhibit_and_late_result(rig):
    c, _, agent, _, base, _, _ = rig
    gid, goal, exhibit = request(rig)
    prepared = prepare(goal, exhibit, agent["id"], now=20)
    payload = finalize(prepared, goal, base)
    assert c.patch(f"/api/goals/{gid}", json={"status": "cancelled"}).status_code == 200
    fresh = call(c, agent, "GET", f"/api/agent/goals/{gid}").json()
    with pytest.raises(Refused):
        finalize(prepared, fresh, base)
    share = goal["binding"]["share_ids"][0]
    assert call(c, agent, "GET", f"/api/agent/shares/{share}/atoms").status_code == 410
    assert call(c, agent, "POST", f"/api/agent/goals/{gid}/result", payload).status_code == 409
    assert call(c, agent, "POST", f"/api/agent/goals/{gid}/cancel-ack").status_code == 200


def test_wrong_worker_partial_exhibit_and_expired_claim_refused(rig):
    _, _, agent, other, base, _, _ = rig
    _, goal, exhibit = request(rig)
    with pytest.raises(Refused):
        prepare(goal, exhibit, other["id"], now=20)
    for key, value in [("complete", False), ("offset", 1), ("body", "{}"), ("share_id", "unbound")]:
        changed = copy.deepcopy(exhibit)
        changed[key] = value
        with pytest.raises(Refused):
            prepare(goal, changed, agent["id"], now=20)
    prepared = prepare(goal, exhibit, agent["id"], now=20)
    for field in ("lease_until", "deadline_at"):
        expired = copy.deepcopy(goal)
        expired[field] = "2000-01-01T00:00:00Z"
        with pytest.raises(Refused):
            finalize(prepared, expired, base)


def test_result_that_grants_authority_refused_by_host(rig):
    c, _, agent, _, base, _, _ = rig
    gid, goal, exhibit = request(rig)
    prepared = prepare(goal, exhibit, agent["id"], now=20)
    payload = finalize(prepared, goal, base)
    payload["data"]["proposal"]["authority"] = "execute"
    response = call(c, agent, "POST", f"/api/agent/goals/{gid}/result", payload)
    assert response.status_code == 422, response.text
