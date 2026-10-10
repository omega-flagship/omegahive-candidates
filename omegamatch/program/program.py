"""Match-owned semantic hook candidate. No stores, ranking or side effects.

ctx.validation_context(goal) is the generic host API being prepared;
ctx.catalogue(scope) is still pending and its Match record shape is proposed.
The current host calls synchronously, using ctx.validation; generic context
method is supported when supplied. Async resolver values are refused.
It must resolve current requester-visible facts inside the host completion
transaction. A missing/failed resolver refuses completion, never defaults open.
"""
import inspect
import importlib.util
import hashlib
from pathlib import Path
import sys
import json
# Load the reviewed sibling by content-derived module identity. All code needed
# for validation lives in this folder and is covered by the host package digest.
_protocol_path = Path(__file__).with_name('protocol.py')
_protocol_name = '_omegamatch_protocol_' + hashlib.sha256(_protocol_path.read_bytes()).hexdigest()
if _protocol_name not in sys.modules:
    _spec = importlib.util.spec_from_file_location(_protocol_name, _protocol_path)
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_protocol_name] = _module
    try:
        _spec.loader.exec_module(_module)
    except Exception:
        sys.modules.pop(_protocol_name, None)
        raise
_protocol = sys.modules[_protocol_name]
ReuseAdmission, Refused = _protocol.ReuseAdmission, _protocol.Refused


def describe():
    return {'contract':'0.1',
            'kinds':[{'id':'status','label':'Admission status','role':'assessment'}],
            'relations':[], 'actions':[]}


def view(ctx, focus=None, stage=None):
    return {'revision':'admission-candidate-v1',
            'items':[{'id':'admission-status','kind':'status',
                      'label':'Host-owned Match context required; integration pending'}],
            'links':[], 'focus':'admission-status'}


def act(ctx, action, items, params=None, base_revision=None):
    return {'status':'refused','message':'Admission runs only through the host result hook.'}


def _error(code):
    return {'errors':[code]}


def validate_result(ctx, goal, proposal):
    """Return ok/errors only; acceptance remains with requester or Planner.

    Proposed catalogue record:
    {goal_id, request_id, active, binding, current_binding, need_id,
     visible_offers, evidence, host_candidates, required_conditions?}.
    All are host-derived; neither proposal nor model-supplied fields may
    populate them. The resolver is responsible for visibility and custody.
    """
    resolver=getattr(ctx,'validation_context',None)
    catalogue=getattr(ctx,'catalogue',None)
    if not callable(catalogue) or not hasattr(ctx,'viewer_for_requester'):
        return _error('match_host_context_unavailable')
    try:
        if not isinstance(goal,dict) or not isinstance(goal.get('id'),str):
            return _error('invalid_host_goal')
        binding=goal.get('binding')
        if isinstance(binding,str):
            binding=json.loads(binding)
        if not isinstance(binding,dict) or not isinstance(binding.get('request_id'),str):
            return _error('goal_request_binding_missing')
        context=resolver(goal) if callable(resolver) else getattr(ctx,'validation',None)
        if inspect.isawaitable(context):
            if inspect.iscoroutine(context):
                context.close()
            return _error('async_host_context_unsupported')
        if (not isinstance(context,dict) or context.get('goal',{}).get('id')!=goal['id']
                or context.get('request',{}).get('id')!=binding['request_id']):
            return _error('host_request_mismatch')
        state=context.get('request_state',context.get('request',{}).get('state'))
        if state not in {'accepted','queued','working','needs-approval'}:
            return _error('request_inactive')
        requester=context.get('requester_swarm')
        source_swarm=context.get('request',{}).get('from_swarm')
        if not isinstance(requester,str) or not requester:
            return _error('requester_scope_missing')
        if source_swarm is not None and source_swarm != requester:
            return _error('requester_scope_mismatch')
        record=catalogue(requester)
        if inspect.isawaitable(record):
            if inspect.iscoroutine(record):
                record.close()
            return _error('async_host_context_unsupported')
        if not isinstance(record,dict):
            return _error('invalid_host_context')
        # Draft 1 projects offers, not request-specific admission witnesses.
        # An empty projection is not a zero-candidate search receipt either.
        if 'offers' in record and 'catalogue_digest' in record:
            return _error('match_semantic_context_unavailable')
        if record.get('goal_id')!=goal['id'] or record.get('request_id')!=binding['request_id']:
            return _error('host_request_mismatch')
        if record['binding']['request_id']!=binding['request_id']:
            return _error('host_request_mismatch')
        common=dict(binding=record['binding'],current_binding=record['current_binding'],active=record['active'])
        kind=proposal.get('kind') if isinstance(proposal,dict) else None
        if kind == 'typed-need':
            _protocol.admit_typed_need(proposal,source_need=record['source_need'],
                                       known_operations=record['known_operations'],**common)
        elif kind == 'no-candidate':
            _protocol.admit_no_candidate(proposal,need_id=record['need_id'],
                                         search_receipt=record['search_receipt'],**common)
        else:
            admission=ReuseAdmission(
                binding=record['binding'],need_id=record['need_id'],
                visible_offers=record['visible_offers'],evidence=record['evidence'],
                host_candidates=record['host_candidates'],
                required_conditions=record.get('required_conditions',()),
            )
            admission.admit(proposal,current_binding=record['current_binding'],active=record['active'])
        return {'ok':True}
    except Refused as exc:
        return _error(str(exc))
    except Exception:
        # Do not disclose internal paths, hidden offers or provider context.
        return _error('match_host_context_invalid_or_unavailable')
