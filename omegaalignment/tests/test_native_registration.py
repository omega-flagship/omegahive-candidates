"""Registration against an isolated host: no listening server or mind execution."""
import json
import os
from pathlib import Path

from hive.tests.test_core_api import client  # noqa: F401
from omegaalignment.swarm import blueprint


def test_native_candidate_persists_without_start_or_access(client):
    candidate = blueprint()
    response = client.post("/api/swarms", json=candidate["swarm"])
    assert response.status_code == 200, response.text
    swarm_id = response.json()["id"]
    budget = client.post("/api/budgets", json={"scope": "swarm:" + swarm_id,
                        "period": "month", "limit_usd": 0, "note": "Inert Alignment qualification"})
    assert budget.status_code == 200, budget.text
    assert budget.json()["limit_usd"] == 0
    assert budget.json()["scope"] == "swarm:" + swarm_id and budget.json()["period"] == "month"
    roles, minds = {}, {}
    hive = client.app.state.hive
    for definition in candidate["roles"]:
        response = client.post("/api/roles", json=definition["fields"])
        assert response.status_code == 200, response.text
        roles[definition["key"]] = response.json()["id"]
        stored = next(r for r in client.get("/api/roles").json() if r["id"] == response.json()["id"])
        for field in ("prompt", "mandate", "default_model", "default_budget", "rules"):
            assert stored[field] == definition["fields"][field]
    for definition in candidate["minds"]:
        response = client.post("/api/agents", json={**definition, "swarm_id": swarm_id,
                            "role_id": roles[definition["role_key"]]})
        assert response.status_code == 200, response.text
        member = client.get("/api/agents/" + response.json()["id"]).json()
        assert member["kind"] == "omega"
        assert member["status"] == "created"
        assert member["model"] == "mock/echo" and member["budget_usd"] == 0
        assert member["role_id"] == roles[definition["role_key"]]
        minds[definition["role_key"]] = member["id"]
        for skill in ("hive-request", "hive-finding", "hive-review-complete", "hive-lifecycle-start",
                      "hive-publish", "read-file", "shell", "metta", "web-search"):
            assert hive.policy.decide(hive.agent(member["id"]), skill)[0] == "deny"
    assert client.put(f"/api/swarms/{swarm_id}/services", json={"kinds": []}).status_code == 200
    response = client.patch(f"/api/swarms/{swarm_id}", json={"coordinator_id": minds["coordinator"]})
    assert response.status_code == 200, response.text
    stored = client.get(f"/api/swarms/{swarm_id}").json()
    assert stored["coordinator_id"] == minds["coordinator"]
    assert set(stored["member_ids"]) == set(minds.values()) and stored["services"] == []
    assert not any(call[0] == "start" for call in client.supervisor.calls)
    assert hive.db.one("SELECT COUNT(*) AS n FROM usage")["n"] == 0
    assert hive.db.one("SELECT COUNT(*) AS n FROM delegations")["n"] == 0
    receipt_path = os.environ.get("ALIGNMENT_QUALIFICATION_RECEIPT")
    if receipt_path:
        Path(receipt_path).write_text(json.dumps({
            "evidence_level": "isolated-host-registration-fake-supervisor",
            "host_commit": os.environ["ALIGNMENT_HOST_COMMIT"],
            "configuration_digest": candidate["configuration_digest"],
            "native_members": 3, "role_field_persistence": "verified",
            "coordinator_selection": "verified", "policy_probes_denied": 27,
            "monthly_swarm_budget_usd": 0, "member_budgets_usd": [0, 0, 0],
            "services": [], "start_calls": 0, "usage_rows": 0, "delegations": 0,
            "live_registration": "not-established-by-this-test",
            "role_procedure_trial": "not-run", "behavior_assessment": "not-run",
        }, indent=2) + "\n")
