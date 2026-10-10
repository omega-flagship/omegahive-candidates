"""Pure structural wiring analysis. OmegaAtom owns envelope and lineage semantics.

All inputs are supplied projections. Neither hashes nor conformance claims
establish authentication, availability, Lab admission or execution authority.
"""
import copy
import hashlib
import json
import re
from graphlib import TopologicalSorter, CycleError

from omegaatom import Refused, validate, lineage_state, format_evidence_ref


def require(ok, message):
    if not ok:
        raise Refused(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def token(value):
    require(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:/@+-]{0,127}', value), 'invalid identifier')
    return value


def sha(value):
    require(isinstance(value, str) and re.fullmatch('[a-f0-9]{64}', value), 'invalid SHA-256')
    return value


def fields(value, names):
    require(isinstance(value, dict) and set(value) == set(names.split()), 'fields mismatch: ' + names)


def bounded(value):
    try:
        require(len(json.dumps(value, allow_nan=False).encode()) <= 200_000, 'input exceeds 200 KB')
    except (TypeError, ValueError, RecursionError) as exc:
        raise Refused(str(exc)) from exc


def slots_index(slots):
    """Read-only exact contract projection supplied from Root; never a registry."""
    bounded(slots)
    require(isinstance(slots, list) and len(slots) <= 100, 'slot list bound')
    result = {}
    for slot in slots:
        fields(slot, 'id family input_schema result_schema suite')
        for k in ('id', 'family', 'suite'):
            token(slot[k])
        for k in ('input_schema', 'result_schema'):
            sha(slot[k])
        require(slot['id'] not in result, 'duplicate slot')
        result[slot['id']] = dict(slot, contract=digest(slot))
    return result


def validate_manifest(manifest, slots):
    """Closed L0 wiring projection of a D1 manifest, with explicit need modes."""
    bounded(manifest)
    index = slots_index(slots)
    fields(manifest, 'schema id version provides consumes effects entrypoints source_pins licence adaptor')
    require(manifest['schema'] == 'omegagraft-plug/0.1', 'unsupported plug schema')
    for k in ('id', 'version', 'licence'):
        token(manifest[k])
    require(type(manifest['adaptor']) is bool, 'adaptor must be boolean')
    for k in ('provides', 'consumes', 'effects'):
        require(isinstance(manifest[k], list) and len(manifest[k]) <= 100, 'manifest list bound')
    seen = set()
    for p in manifest['provides']:
        fields(p, 'slot contract')
        token(p['slot']); sha(p['contract'])
        require(p['slot'] in index and p['contract'] == index[p['slot']]['contract'], 'provider contract mismatch')
        require(p['slot'] not in seen, 'duplicate provides')
        seen.add(p['slot'])
    seen = set()
    for n in manifest['consumes']:
        fields(n, 'slot contract mode primary fallbacks')
        token(n['slot']); sha(n['contract']); token(n['primary'])
        require(n['slot'] in index and n['contract'] == index[n['slot']]['contract'], 'need contract mismatch')
        require(isinstance(n['mode'], str) and n['mode'] in {'required', 'degrade', 'optional'}, 'invalid need mode')
        require(isinstance(n['fallbacks'], list) and len(n['fallbacks']) <= 16, 'fallback list bound')
        for p in n['fallbacks']:
            token(p)
        require(len(set(n['fallbacks'])) == len(n['fallbacks']) and n['primary'] not in n['fallbacks'], 'duplicate fallback')
        require(n['mode'] == 'degrade' or not n['fallbacks'], 'fallback only allowed for degrade')
        require(manifest['id'] not in [n['primary'], *n['fallbacks']], 'self need refused')
        require(n['slot'] not in seen, 'duplicate need')
        seen.add(n['slot'])
    for effect in manifest['effects']:
        token(effect)
    require(isinstance(manifest['entrypoints'], dict) and manifest['entrypoints'], 'entrypoints required')
    for deployment, reference in manifest['entrypoints'].items():
        require(deployment in {'library', 'native-skill', 'app', 'service', 'mind', 'swarm', 'mcp', 'federated'}, 'unknown deployment')
        token(reference)  # Reference only: never import or dereference.
    require(isinstance(manifest['source_pins'], dict) and manifest['source_pins'], 'source pins required')
    for reference, pin in manifest['source_pins'].items():
        token(reference); sha(pin)
    return copy.deepcopy(manifest)


def manifest_atoms(manifest, slots):
    """Return statement data only. Host supplies real evidence ids and envelopes."""
    m = validate_manifest(manifest, slots)
    mid = m['id']
    result = [['Plug', mid, m['version'], digest(m), 'adaptor' if m['adaptor'] else 'module']]
    result += [['Provides', mid, p['slot'], p['contract']] for p in m['provides']]
    result += [['Needs', mid, n['slot'], n['contract'], n['mode'], n['primary'], n['fallbacks']] for n in m['consumes']]
    result += [['Effect', mid, e] for e in m['effects']]
    return result


def _read(snapshot, slots):
    snapshot = validate(snapshot)  # The shared validator is authoritative.
    slots = slots_index(slots)
    states = {tuple(s['id']): s for s in lineage_state(snapshot)}
    plugs, provides, needs, bounds, conforms, evidence = {}, {}, {}, {}, {}, []
    for r in snapshot['records']:
        s = states[tuple(r['id'])]
        if s['retracted'] or s['stale'] or r['unknown']:
            continue
        # Predictions and inferred advice cannot become a structural binding.
        if r['status'] not in {'observed', 'simulated'} or r['truth'][1] != 1:
            continue
        a = r['statement']; head = a[0]
        arities = {'Plug': 5, 'Provides': 4, 'Needs': 7, 'Bound': 4, 'Conforms': 7, 'Effect': 3}
        if not isinstance(head, str) or head not in arities:
            continue  # Health/TrackRecord and unrelated atoms remain in the snapshot.
        require(len(a) == arities[head], 'wiring atom arity mismatch')
        for position, x in enumerate(a[1:], 1):
            if not (head == 'Needs' and position == 6):
                token(x)
        evidence.append(format_evidence_ref(r['id']))
        if head == 'Plug':
            _, mid, version, pin, kind = a
            sha(pin); require(kind in {'module', 'adaptor'}, 'invalid plug kind')
            require(mid not in plugs, 'ambiguous plug')
            plugs[mid] = {'version': version, 'digest': pin, 'kind': kind}
        elif head == 'Provides':
            _, mid, slot, contract = a
            require(slot in slots and contract == slots[slot]['contract'], 'provider contract mismatch')
            require((mid, slot) not in provides, 'duplicate provides atom')
            provides[mid, slot] = contract
        elif head == 'Needs':
            _, mid, slot, contract, mode, primary, fallbacks = a
            require(slot in slots and contract == slots[slot]['contract'], 'need contract mismatch')
            require(mode in {'required', 'degrade', 'optional'}, 'invalid need mode')
            require(isinstance(fallbacks, list) and len(fallbacks) <= 16, 'fallback list bound')
            for p in fallbacks:
                token(p)
            require(len(set(fallbacks)) == len(fallbacks) and primary not in fallbacks, 'duplicate fallback')
            require(mode == 'degrade' or not fallbacks, 'fallback only allowed for degrade')
            require((mid, slot) not in needs, 'ambiguous need')
            needs[mid, slot] = {'mode': mode, 'primary': primary, 'fallbacks': fallbacks}
        elif head == 'Bound':
            _, mid, slot, provider = a
            require((mid, slot) not in bounds, 'ambiguous binding')
            bounds[mid, slot] = provider
        elif head == 'Conforms':
            _, mid, slot, version, pin, suite, outcome = a
            sha(pin); require(outcome in {'pass', 'fail'}, 'invalid conformance outcome')
            require((mid, slot) not in conforms, 'ambiguous conformance')
            conforms[mid, slot] = (version, pin, suite, outcome)
    require(len(plugs) <= 100, 'module bound exceeded')
    for mid, slot in provides:
        require(mid in plugs, 'Provides without Plug')
    deps = {mid: set() for mid in plugs}
    for (mid, slot), n in needs.items():
        require(mid in plugs, 'Needs without Plug')
        # Include every declared fallback and explicit binding: latent cycles refuse.
        for p in [n['primary'], *n['fallbacks'], bounds.get((mid, slot), n['primary'])]:
            require(p != mid, 'cyclic self need')
            if p in plugs:
                deps[mid].add(p)
    for key, provider in bounds.items():
        require(key in needs, 'Bound without Needs')
        require((provider, key[1]) in provides, 'Bound provider does not provide slot')
    try:
        order = list(TopologicalSorter(deps).static_order())
    except CycleError as exc:
        raise Refused('cyclic need refused') from exc
    eligible = set()
    for key in provides:
        mid, slot = key
        expected = (plugs[mid]['version'], plugs[mid]['digest'], slots[slot]['suite'], 'pass')
        if conforms.get(key) == expected:
            eligible.add(key)
    return snapshot, slots, plugs, needs, bounds, eligible, order, evidence


def binding_graph(snapshot, slots, absent=()):
    """Compute a deterministic advisory graph; never pick an unrequested provider."""
    s, si, plugs, needs, bounds, eligible, order, evidence = _read(snapshot, slots)
    require(isinstance(absent, (tuple, list, set)) and all(isinstance(x, str) for x in absent), 'invalid absent modules')
    missing = set(absent)
    require(missing <= plugs.keys(), 'unknown unplug target')
    modules, edges, absence = {}, [], []
    for mid in order:
        state = 'absent' if mid in missing else 'running'
        for (consumer, slot), n in sorted(needs.items()):
            if consumer != mid:
                continue
            primary = bounds.get((mid, slot), n['primary'])
            candidates = [primary, *[p for p in n['fallbacks'] if p != primary]]
            available = lambda p: (p, slot) in eligible and modules.get(p) not in {None, 'absent', 'paused'}
            chosen = next((p for p in candidates if available(p)), None)
            outcome = 'bound' if chosen == primary else 'fallback' if chosen else {'required': 'paused', 'degrade': 'unavailable', 'optional': 'omitted'}[n['mode']]
            if state != 'absent':
                if outcome == 'paused':
                    state = 'paused'
                elif outcome in {'fallback', 'unavailable'} and state != 'paused':
                    state = 'degraded'
            edges.append({'consumer': mid, 'slot': slot, 'mode': n['mode'], 'requested': primary, 'provider': chosen, 'outcome': outcome})
            if chosen != primary:
                absence.append(['Unavailable', mid, slot, primary, outcome])
        modules[mid] = state
    return {'level': 'L0', 'authority': 'none', 'base_digest': digest(s), 'catalogue_digest': digest(slots),
            'modules': dict(sorted(modules.items())), 'edges': sorted(edges, key=lambda e: (e['consumer'], e['slot'])),
            'absence_statements': sorted(absence),
            'evidence_refs': sorted(evidence)}


def blast_radius(snapshot, slots, module):
    before = binding_graph(snapshot, slots)
    after = binding_graph(snapshot, slots, [module])
    changed = [m for m in after['modules'] if before['modules'][m] != after['modules'][m]]
    changed_edges = [e for e in after['edges'] if e not in before['edges']]
    return {'level': 'L0', 'authority': 'none', 'unplug': module, 'affected': changed,
            'changed_edges': changed_edges, 'before': before, 'after': after,
            'steps': ['drain', 'unbind-after-owner-approval', 'verify-consumers']}


def propose_swap(snapshot, slots, consumer, slot, provider):
    s, si, plugs, needs, bounds, eligible, order, evidence = _read(snapshot, slots)
    require((consumer, slot) in needs, 'unknown consumer need')
    require((provider, slot) in eligible, 'target lacks exact slot conformance pass')
    current = binding_graph(snapshot, slots)
    edge = next(e for e in current['edges'] if e['consumer'] == consumer and e['slot'] == slot)
    old = edge['provider']
    require(old is not None and old != provider, 'swap requires distinct usable rollback provider')
    require(current['modules'][consumer] not in {'absent', 'paused'}, 'consumer is not running')
    require(current['modules'][provider] not in {'absent', 'paused'}, 'candidate is not running')
    # Analyze the alternate edge without changing the supplied snapshot or grants.
    deps = {m: set() for m in plugs}
    for (m, sl), n in needs.items():
        for p in [n['primary'], *n['fallbacks'], bounds.get((m, sl), n['primary'])]:
            if p in plugs:
                deps[m].add(p)
    deps[consumer].add(provider)
    try:
        tuple(TopologicalSorter(deps).static_order())
    except CycleError as exc:
        raise Refused('swap introduces cyclic need') from exc
    return {'level': 'L0', 'authority': 'none', 'status': 'proposal',
            'base_digest': digest(s), 'catalogue_digest': digest(slots),
            'consumer': consumer, 'slot': slot, 'candidate': dict(plugs[provider], id=provider),
            'rollback_target': dict(plugs[old], id=old), 'evidence_refs': sorted(evidence),
            'steps': ['shadow', 'compare-with-Bench', 'owner-approval', 'canary', 'bind', 'observe', 'rollback-by-rebinding'],
            'proposed_statement': ['Bound', consumer, slot, provider],
            'rollback_statement': ['Bound', consumer, slot, old],
            'required_gates': ['Lab-admission', 'Bench-comparison', 'five-answer-approval', 'named-admin-attachment', 'update-hold', 'fresh-binding-and-policy-check'],
            'unresolved': ['authenticated-custody', 'runtime-health', 'budget', 'owner-adoption']}
