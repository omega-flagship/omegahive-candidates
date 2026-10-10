"""Contextual evidence reports only. No acceptance, ranking or authority decisions."""
from copy import deepcopy

CONTEXT_FIELDS = frozenset({'requester', 'provider', 'generation', 'skill', 'source_digest',
                            'catalogue_digest', 'policy_revision'})
AXES = ('configured', 'loaded', 'callable', 'policy', 'structural-fit', 'performance')


def _context(value):
    if not isinstance(value, dict) or set(value) != CONTEXT_FIELDS:
        raise ValueError('invalid evidence context')
    if not all(isinstance(v, str) and v and len(v.encode()) <= 8192 for v in value.values()):
        raise ValueError('invalid context value')


def readiness_report(context, observations):
    """Report supplied host-resolved observations without changing their meaning.

    Caller must enforce visibility/custody. This function cannot authenticate a
    record, manufacture a receipt, establish absence or authorize execution.
    Evidence outside the exact context is omitted, not exposed as hidden history.
    """
    _context(context)
    if not isinstance(observations, list) or len(observations) > 10000:
        raise ValueError('invalid observation collection')
    buckets = {axis: {} for axis in AXES}
    identities = {}
    for observation in observations:
        if not isinstance(observation, dict): raise ValueError('invalid observation')
        _context(observation.get('context'))
        if observation['context'] != context:
            continue
        if set(observation) != {'context', 'axis', 'stance', 'ref', 'digest', 'origin'}:
            raise ValueError('invalid observation fields')
        axis, stance = observation['axis'], observation['stance']
        if axis not in AXES or stance not in {'supported', 'contradicted'}:
            raise ValueError('invalid observation stance')
        if not all(isinstance(observation[k], str) and observation[k] for k in ('ref', 'digest', 'origin')):
            raise ValueError('unresolved evidence identity')
        ref = observation['ref']
        identity = (observation['digest'], observation['origin'])
        if ref in identities and identities[ref] != identity:
            raise ValueError('conflicting evidence identity')
        identities[ref] = identity
        key = (ref, stance)
        buckets[axis][key] = {k: observation[k] for k in ('stance', 'ref', 'digest', 'origin')}
    conditions = {}
    for axis in AXES:
        evidence = [buckets[axis][key] for key in sorted(buckets[axis])]
        stances = {item['stance'] for item in evidence}
        status = 'conflicting' if len(stances) == 2 else next(iter(stances), 'unknown')
        conditions[axis] = {'status': status, 'evidence': evidence,
                            'reason': 'no-applicable-record' if not evidence else 'supplied-contextual-evidence'}
    return {'context': deepcopy(context), 'conditions': conditions,
            'classification': 'explanation-only', 'acceptance': 'pending',
            'execution_authorized': False}
