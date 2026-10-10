"""Reuse-alert shape in the host's strict JSON Schema subset.

No conditional keywords: code/service locator semantics and evidence custody
remain in admission. Per-request bindings are supplied by trusted host code.
"""
from copy import deepcopy
from .protocol import BINDING_FIELDS, BASES, _binding


def _text(maximum=512):
    return {'type':'string','minLength':1,'maxLength':maximum,'pattern':r'\S'}


def _object(properties, required=None):
    return {'type':'object','properties':properties,
            'required':list(properties) if required is None else required,
            'additionalProperties':False}


def reuse_alert_schema(binding=None, need_id=None):
    binding_properties={k:_text() for k in sorted(BINDING_FIELDS)}
    binding_properties['need_revision']={'type':'integer','minimum':1}
    binding_schema=_object(binding_properties)
    if binding is not None:
        _binding(binding)
        binding_schema['const']=deepcopy(binding)
    ref_properties={k:_text(2048 if k=='context' else 512)
                    for k in ('id','digest','context','observed_at','origin_id','verdict','mandate')}
    ref_properties['basis']={'type':'string','enum':sorted(BASES)}
    reference=_object(ref_properties,['id','digest','basis','context','observed_at'])
    fields={
        'kind':{'type':'string','const':'reuse-alert'},
        'binding':binding_schema,
        'need_id':_text(), 'offer_id':_text(), 'provider_id':_text(),
        'target_kind':{'type':'string','enum':['code','service']},
        'locator':_object({k:_text(2048) for k in ('workspace','symbol','service')},[]),
        'artifact_digest':_text(),
        'contract_fit':{'type':'string','enum':['supported','possible','conflicting']},
        'evidence_refs':{'type':'array','minItems':1,'maxItems':32,'items':reference},
        'unresolved_conditions':{'type':'array','maxItems':64,'items':_text(1024)},
        'rationale':_text(4000),
        'suggested_next_step':{'type':'string','enum':[
            'inspect-existing-code','ask-existing-service','consider-connection']},
        'authority':{'type':'string','const':'recommendation-only'},
    }
    if need_id is not None:
        if not isinstance(need_id,str) or not need_id.strip():
            raise ValueError('invalid_need')
        fields['need_id']['const']=need_id
    schema=_object(fields)
    schema['title']='OmegaMatch reuse alert v0.1'
    return schema


def _context_binding(binding=None):
    return reuse_alert_schema(binding)['properties']['binding']


def _text_list(required=False):
    return {'type':'array','minItems':1 if required else 0,'maxItems':64,'items':_text(1024)}


def typed_need_schema(binding=None):
    refs=_object({key:_text() for key in ('id','digest')})
    schema=_object({
        'kind':{'type':'string','const':'typed-need'},'binding':_context_binding(binding),
        'operation':_text(),'inputs':_text_list(True),'required_outputs':_text_list(True),
        'hard_constraints':{'type':'object','maxProperties':32},
        'preferences':{'type':'object','maxProperties':32},
        'prerequisites':_text_list(),'assumptions':_text_list(),'unknowns':_text_list(),
        'alternatives':_text_list(),'source_refs':{'type':'array','minItems':1,'maxItems':32,'items':refs},
        'interpretation_status':{'type':'string','const':'proposed'},
    })
    schema['title']='OmegaMatch proposed typed need v0.1'
    return schema


def no_candidate_schema(binding=None):
    schema=_object({
        'kind':{'type':'string','const':'no-candidate'},'binding':_context_binding(binding),
        'need_id':_text(),'searched_scope':_text_list(True),'unknowns':_text_list(),
        'search_complete':{'type':'boolean'},
        'truncation_reason':{'type':['string','null'],'minLength':1,'maxLength':1024},
    })
    schema['title']='OmegaMatch scoped no-candidate result v0.1'
    return schema


def match_result_schema(binding=None):
    """Host-subset union shape; conditional obligations require semantic hook.

    The host subset has no oneOf. Its generic gate only checks bounded fields;
    the companion enforces the exact field set and meaning for the selected kind.
    This schema must be paired with validate: program:omegamatch.
    """
    props={}
    for schema in (reuse_alert_schema(binding),typed_need_schema(binding),no_candidate_schema(binding)):
        props.update(deepcopy(schema['properties']))
    props['kind']={'type':'string','enum':['typed-need','reuse-alert','no-candidate']}
    schema=_object(props,['kind','binding'])
    schema['title']='OmegaMatch result v0.1; semantic companion required'
    return schema
