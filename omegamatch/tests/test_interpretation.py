from copy import deepcopy
import pytest
from omegamatch.protocol import admit_typed_need,admit_no_candidate,Refused
from omegamatch.schema import typed_need_schema,no_candidate_schema
from omegamatch.tests.test_protocol import fixture
from omegamatch.tests.test_schema import host


def typed():
    inputs,_=fixture();binding=inputs['binding']
    source={'hard_constraints':{'network':'offline'},'preferences':{'language':'python'},
            'source_refs':[{'id':'source-1','digest':'source-v1'}],'unknowns':['scale unknown']}
    output={'kind':'typed-need','binding':binding,'operation':'csv-to-table','inputs':['Csv'],
            'required_outputs':['Table'],'hard_constraints':deepcopy(source['hard_constraints']),
            'preferences':deepcopy(source['preferences']),'source_refs':deepcopy(source['source_refs']),
            'prerequisites':[],'assumptions':['input contains header'],'unknowns':['scale unknown'],
            'alternatives':[],'interpretation_status':'proposed'}
    args=dict(binding=binding,current_binding=deepcopy(binding),source_need=source,known_operations=['csv-to-table'])
    return output,args


def absent():
    inputs,_=fixture();binding=inputs['binding']
    search=dict(candidate_count=0,searched_scope=['visible:invented-swarm'],search_complete=False,
                truncation_reason='search budget exhausted',unknowns=['other scopes not searched'])
    output={'kind':'no-candidate','binding':binding,'need_id':'need-1',**{k:v for k,v in search.items() if k!='candidate_count'}}
    args=dict(binding=binding,current_binding=deepcopy(binding),need_id='need-1',search_receipt=search)
    return deepcopy(output),args


def test_typed_need_remains_proposal_and_has_host_valid_shape():
    output,args=typed();schema=typed_need_schema(args['binding'])
    host.check_schema(schema);assert host.validate(output,schema)==[]
    result=admit_typed_need(output,**args)
    assert result.acceptance=='pending' and result.execution_authorized is False


@pytest.mark.parametrize('field,value',[
    ('hard_constraints',{'network':'online'}),('preferences',{}),('source_refs',[]),
    ('operation','hidden-service'),('unknowns',[]),('interpretation_status','accepted'),
])
def test_interpretation_cannot_rewrite_source_or_authority(field,value):
    output,args=typed();output[field]=value
    with pytest.raises(Refused):admit_typed_need(output,**args)


def test_inferred_requirement_cannot_be_added_as_source_constraint():
    output,args=typed();output['hard_constraints']['header']=True
    with pytest.raises(Refused,match='source_constraints_or_provenance_changed'):
        admit_typed_need(output,**args)


def test_truncated_search_has_bounded_scope_and_no_authority():
    output,args=absent();schema=no_candidate_schema(args['binding'])
    host.check_schema(schema);assert host.validate(output,schema)==[]
    result=admit_no_candidate(output,**args)
    assert result.result['search_complete'] is False and result.acceptance=='pending'


@pytest.mark.parametrize('field,value',[
    ('searched_scope',['all-hives']),('search_complete',True),('truncation_reason',None),('unknowns',[]),
])
def test_no_candidate_cannot_overclaim_scope_or_erase_limits(field,value):
    output,args=absent();output[field]=value
    with pytest.raises(Refused):admit_no_candidate(output,**args)


def test_no_candidate_refused_when_host_found_offers():
    output,args=absent();args['search_receipt']['candidate_count']=1
    with pytest.raises(Refused,match='candidates_exist'):admit_no_candidate(output,**args)


def test_completed_visible_search_is_not_global_absence():
    output,args=absent()
    for record in (output,args['search_receipt']):record.update(search_complete=True,truncation_reason=None)
    assert admit_no_candidate(output,**args).result['searched_scope']==['visible:invented-swarm']


def test_new_boundaries_refuse_stale_context_and_extra_execution_fields():
    for maker,admit in ((typed,admit_typed_need),(absent,admit_no_candidate)):
        output,args=maker();args['current_binding']['policy_revision']='new'
        with pytest.raises(Refused,match='stale_snapshot'):admit(output,**args)
        output,args=maker();output['execute']=True
        with pytest.raises(Refused,match='invalid_result_fields'):admit(output,**args)


def test_all_result_kinds_reach_companion_with_host_context():
    from omegamatch.tests.test_program import Context
    from omegamatch.program.program import validate_result
    from omegamatch.schema import match_result_schema
    for maker in (typed,absent):
        output,args=maker()
        record={k:v for k,v in args.items() if k!='current_binding'}
        record.update(current_binding=args['current_binding'],active=True,
                      goal_id='goal-1',request_id=args['binding']['request_id'])
        goal={'id':'goal-1','binding':{'request_id':record['request_id']}}
        ctx=Context(record)
        schema=match_result_schema(args['binding'])
        host.check_schema(schema);assert host.validate(output,schema)==[]
        assert validate_result(ctx,goal,output)=={'ok':True}
        output['unknowns']=[]
        assert validate_result(ctx,goal,output)=={'errors':['uncertainty_erased']}


def test_composite_shape_requires_semantic_checker_for_kind_fields():
    from omegamatch.schema import match_result_schema
    from omegamatch.program.program import validate_result
    from omegamatch.tests.test_program import Context
    output,args=typed();schema=match_result_schema(args['binding'])
    del output['source_refs']
    assert host.validate(output,schema)==[]  # subset has no conditional keywords
    record={**args,'goal_id':'goal-1','request_id':args['binding']['request_id'],'active':True}
    goal={'id':'goal-1','binding':{'request_id':record['request_id']}}
    assert validate_result(Context(record),goal,output)=={'errors':['invalid_result_fields']}
