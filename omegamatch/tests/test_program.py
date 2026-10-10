import asyncio
from copy import deepcopy
import pytest
from omegamatch.program.program import validate_result
from omegamatch.swarm import blueprint
from omegamatch.tests.test_protocol import fixture


class Context:
    def __init__(self,record): self.record=record
    viewer_for_requester='invented-requester-view'
    def validation_context(self,goal):
        return {'goal':goal,'request':{'id':self.record['request_id']},'request_state':'working','requester_swarm':'requester-swarm'}
    def catalogue(self,scope):
        assert scope=='requester-swarm'
        return deepcopy(self.record)


def setup():
    inputs,output=fixture()
    record={**inputs,'goal_id':'goal-1','request_id':inputs['binding']['request_id'],
            'current_binding':deepcopy(inputs['binding']),'active':True}
    goal={'id':'goal-1','binding':{'request_id':inputs['binding']['request_id']}}
    return Context(record),goal,output


def invoke(ctx,goal,output): return validate_result(ctx,goal,output)


def test_valid_hook_has_no_acceptance_or_authority():
    ctx,goal,output=setup()
    assert invoke(ctx,goal,output)=={'ok':True}


def test_missing_host_api_is_closed():
    ctx,goal,output=setup()
    assert invoke(object(),goal,output)=={'errors':['match_host_context_unavailable']}


@pytest.mark.parametrize('field', ['goal_id','request_id'])
def test_context_must_be_for_exact_request_and_goal(field):
    ctx,goal,output=setup();ctx.record[field]='other'
    assert invoke(ctx,goal,output)=={'errors':['host_request_mismatch']}


def test_actual_host_request_cannot_be_invented_by_proposal():
    ctx,goal,output=setup();output['binding']['request_id']='invented'
    assert invoke(ctx,goal,output)=={'errors':['binding_mismatch']}


def test_stale_and_cancelled_host_state_refused():
    ctx,goal,output=setup();ctx.record['current_binding']['catalogue_digest']='new'
    assert invoke(ctx,goal,output)=={'errors':['stale_snapshot']}
    ctx,goal,output=setup();ctx.record['active']=False
    assert invoke(ctx,goal,output)=={'errors':['request_inactive']}


def test_evidence_promotion_refused_by_program():
    ctx,goal,output=setup();output['evidence_refs'][0]['basis']='accepted-performance'
    assert invoke(ctx,goal,output)=={'errors':['evidence_unavailable_or_changed']}


def test_bad_resolver_does_not_leak_context():
    class Broken:
        viewer_for_requester='invented'
        def validation_context(self,goal): raise RuntimeError('secret/private/path')
        def catalogue(self,scope): return {}
    ctx,goal,output=setup()
    assert invoke(Broken(),goal,output)=={'errors':['match_host_context_invalid_or_unavailable']}


def test_async_context_refused_cleanly_for_synchronous_host():
    ctx,goal,output=setup()
    class AsyncContext:
        viewer_for_requester=ctx.viewer_for_requester
        async def validation_context(self,goal): return ctx.validation_context(goal)
        async def catalogue(self,scope): return ctx.record
    assert invoke(AsyncContext(),goal,output)=={'errors':['async_host_context_unsupported']}


def test_native_blueprint_has_no_public_match_service_or_started_modules():
    config=blueprint()
    assert config['services']==[]
    assert config['connection_only_services']==['match']
    assert all(m['kind']=='omega' for m in config['minds'])
    assert config['activation']=='none' and config['budget_usd']==0


@pytest.mark.parametrize('locator', [{}, {'service':'planning'}, {'workspace':'path','symbol':''}])
def test_code_locator_requirements_enforced_in_semantic_hook(locator):
    ctx,goal,output=setup()
    ctx.record['visible_offers']['offer-1']['locator']=locator
    output['locator']=locator
    assert invoke(ctx,goal,output)=={'errors':['invalid_target_locator']}


def test_program_loads_without_workspace_pythonpath(tmp_path):
    import subprocess,sys
    from pathlib import Path
    target=Path(__file__).resolve().parents[1]/'program/program.py'
    code='''import importlib.util,sys,asyncio
spec=importlib.util.spec_from_file_location("standalone_match",sys.argv[1])
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.describe()["contract"]=="0.1"
assert module.validate_result(object(),{},{} )=={"errors":["match_host_context_unavailable"]}
'''
    completed=subprocess.run([sys.executable,'-I','-c',code,str(target)],cwd=tmp_path,capture_output=True,text=True)
    assert completed.returncode==0,completed.stderr


@pytest.mark.parametrize('offers', [[], [{'id':'offer-1','tier':'reviewed'}]])
def test_draft_catalogue_cannot_replace_semantic_witnesses(offers):
    ctx,goal,output=setup()
    ctx.catalogue=lambda scope: {'catalogue_digest':'sha256:draft','offers':offers,'truncated':False}
    assert invoke(ctx,goal,output)=={'errors':['match_semantic_context_unavailable']}


@pytest.mark.parametrize('requester,source,error', [(None,None,'requester_scope_missing'),
                                                     ('other','requester-swarm','requester_scope_mismatch')])
def test_requester_scope_must_be_host_bound(requester,source,error):
    ctx,goal,output=setup()
    ctx.validation_context=lambda g: {'goal':g,'request':{'id':ctx.record['request_id'],'from_swarm':source},
                                     'request_state':'working','requester_swarm':requester}
    ctx.catalogue=lambda scope: pytest.fail('must refuse before catalogue lookup')
    assert invoke(ctx,goal,output)=={'errors':[error]}
