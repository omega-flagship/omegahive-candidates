"""Deterministic interleaving probe on disposable host records.

The synthetic host hook pauses for a real separate thread to cancel the goal
through the host's own update path. It substitutes only the hook decision, not
DB/result code or catalogue behavior. This isolates the persistence race.
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import pytest
from hive.tests.test_core_api import client,agent_headers  # noqa: F401
from omegamatch.tests.host_transport_probes import setup,submit


@pytest.mark.parametrize('changed_status',['cancelled','open'])
def test_lifecycle_change_during_validation_must_not_be_overwritten(client,changed_status):
    asker,mind,request,bound,inputs,output=setup(client,validate='program:synthetic-gate')
    hive=client.app.state.hive
    entered, cancelled = Event(),Event()

    def cancel():
        assert entered.wait(5),'validator was not entered'
        state=hive.goals.update(bound['id'],{'status':changed_status})
        assert state['status']==changed_status
        cancelled.set()

    def synthetic_gate(program_id,goal,proposal):
        assert program_id=='synthetic-gate'
        entered.set()
        assert cancelled.wait(5),'cancellation did not complete'
        return []  # synthetic decision accepted; catalogue not simulated

    original=hive.programs.validate_goal_result
    hive.programs.validate_goal_result=synthetic_gate
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            task=pool.submit(cancel)
            response=submit(client,mind,bound,output)
            task.result(timeout=5)
    finally:
        hive.programs.validate_goal_result=original
    state=client.get(f"/api/agent/goals/{bound['id']}",headers=agent_headers(mind)).json()
    assert state['status']==changed_status,{'response_status':response.status_code,'persisted_status':state['status']}
    assert response.status_code==409,response.text
    assert not state.get('result_data'),state
    assert not any(call[0]=='start' for call in client.supervisor.calls)
