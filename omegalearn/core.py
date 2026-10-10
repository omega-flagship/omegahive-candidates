"""Offline envelope/lineage library. Trusted resolver is supplied by the caller.

No authentication, Atom evidence validation, model execution or adoption is
implemented here. Records are copied at every boundary. Imported text is data.
"""
import hashlib
import json
import re

class Refused(ValueError):
    pass

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def copy(value):
    return json.loads(canonical(value))

def exact(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys.split()):
        raise Refused('unexpected or missing fields')

def word(value):
    if not isinstance(value, str) or not value or len(value) > 512:
        raise Refused('invalid identifier')

def refs(values):
    if not isinstance(values, list) or len(values) > 1000:
        raise Refused('invalid references')
    for v in values: word(v)
    if len(set(values)) != len(values): raise Refused('duplicate reference')

def subject(value):
    exact(value, 'id revision digest')
    word(value['id']); word(value['revision'])
    if not isinstance(value['digest'], str) or not re.fullmatch('[a-f0-9]{64}', value['digest']):
        raise Refused('invalid digest')

def event_shape(event):
    exact(event, 'schema id owner scope subject evidence_refs predictions assumptions review_findings outcome_refs corrections permissions payload')
    if event['schema'] != 'omegalearn/event/1': raise Refused('event schema')
    for k in ('id','owner','scope'): word(event[k])
    subject(event['subject'])
    for k in ('evidence_refs','predictions','assumptions','review_findings','outcome_refs','corrections'): refs(event[k])
    if not event['evidence_refs']: raise Refused('evidence required')
    exact(event['permissions'], 'audiences derive redistribute')
    refs(event['permissions']['audiences'])
    for k in ('derive','redistribute'):
        if type(event['permissions'][k]) is not bool: raise Refused('permission boolean')
    exact(event['payload'], 'kind data')
    if event['payload']['kind'] not in ('error','experience','feedback','knowledge','correction','retraction'):
        raise Refused('payload kind')
    if len(canonical(event).encode()) > 100_000: raise Refused('event too large')

class Ledger:
    """Local dependency projection. Resolver must authenticate source/grants externally."""
    def __init__(self):
        self._events = {}; self._packages = {}; self._stale = set(); self._deliveries = []

    def admit(self, event, resolver):
        event = copy(event); event_shape(event)
        eid = event['id']
        if eid in self._events:
            if self._events[eid] != event: raise Refused('event id conflict')
            return {'id':eid, 'new_evidence':False}
        trusted = resolver(copy(event))
        if not isinstance(trusted, dict) or trusted.get('current_subject') != event['subject']:
            raise Refused('stale or unresolved source')
        if trusted.get('owner') != event['owner'] or trusted.get('scope') != event['scope']:
            raise Refused('source identity mismatch')
        if trusted.get('permissions') != event['permissions']:
            raise Refused('grant mismatch')
        needed = set(sum([event[k] for k in ('evidence_refs','predictions','assumptions','review_findings','outcome_refs')], []))
        if not needed <= set(trusted.get('visible_refs', [])): raise Refused('unresolved evidence/reference')
        if trusted.get('references_valid') is not True: raise Refused('reference chronology/status unverified')
        if any(x not in self._events for x in event['corrections']): raise Refused('unknown correction predecessor')
        key = (event['owner'],event['scope'],canonical(event['subject']))
        if any((e['owner'],e['scope'],canonical(e['subject'])) == key for e in self._events.values()):
            raise Refused('episode alias is not independent evidence')
        seen_evidence = set(sum([e['evidence_refs'] for e in self._events.values()], []))
        new_evidence = bool(set(event['evidence_refs']) - seen_evidence)
        self._events[eid] = event
        for old in event['corrections']: self._stale.add(old)
        return {'id':eid,'new_evidence':new_evidence}

    def invalidate(self, event_id, authorize):
        if event_id not in self._events: raise Refused('unknown source')
        if authorize(copy(self._events[event_id])) is not True: raise Refused('retraction not authorized')
        self._stale.add(event_id)

    def propose(self, package):
        package = copy(package)
        exact(package, 'schema id version kind owner scope source_events evidence_refs provenance_refs evaluation_refs runtime rollback content digest')
        if package['schema'] != 'omegalearn/package/1': raise Refused('package schema')
        for k in ('id','version','owner','scope'): word(package[k])
        if package['kind'] not in ('skill','flow','ontology','pc-net','world-model','rule-set'): raise Refused('package kind')
        for k in ('source_events','evidence_refs','provenance_refs','evaluation_refs'): refs(package[k])
        if not package['source_events']: raise Refused('source events required')
        exact(package['runtime'], 'requires entrypoint'); refs(package['runtime']['requires']); word(package['runtime']['entrypoint'])
        expected = digest({k:v for k,v in package.items() if k != 'digest'})
        if expected != package['digest']: raise Refused('package digest mismatch')
        for eid in package['source_events']:
            if eid not in self._events or eid in self._stale: raise Refused('source absent/stale')
            e = self._events[eid]
            if not e['permissions']['derive'] or package['scope'] not in e['permissions']['audiences']:
                raise Refused('derivation scope refused')
        inherited = set(sum([self._events[e]['evidence_refs'] for e in package['source_events']], []))
        if set(package['evidence_refs']) != inherited: raise Refused('incomplete/invented evidence ancestry')
        if package['kind'] == 'skill':
            exact(package['content'], 'rules procedure track_record_refs')
            refs(package['content']['track_record_refs'])
            if not isinstance(package['content']['rules'], list) or not package['content']['rules']:
                raise Refused('declarative rules required')
            for rule in package['content']['rules']:
                if not isinstance(rule,str) or not rule or len(rule)>10000: raise Refused('invalid rule data')
            exact(package['content']['procedure'],'id steps prerequisites')
            word(package['content']['procedure']['id']); refs(package['content']['procedure']['steps']); refs(package['content']['procedure']['prerequisites'])
        if len(canonical(package).encode()) > 200_000: raise Refused('package too large')
        key = package['id']+'@'+package['version']
        if package['rollback'] is not None:
            exact(package['rollback'], 'id version digest')
            word(package['rollback']['id']); word(package['rollback']['version'])
            if not re.fullmatch('[a-f0-9]{64}', str(package['rollback']['digest'])): raise Refused('rollback digest')
            old = self._packages.get(package['rollback']['id']+'@'+package['rollback']['version'])
            if not old or old['digest'] != package['rollback']['digest']: raise Refused('rollback unresolved')
        if key in self._packages and self._packages[key] != package: raise Refused('immutable version conflict')
        self._packages[key] = package
        return key

    def package(self, key):
        p = copy(self._packages[key]); p['local_status'] = 'stale' if any(e in self._stale for e in p['source_events']) else 'proposed'
        return p

    def deliver(self, key, recipient, artifact_ref, authorize):
        p = self.package(key); word(recipient); word(artifact_ref)
        if p['local_status'] == 'stale': raise Refused('stale package')
        for eid in p['source_events']:
            perms = self._events[eid]['permissions']
            if not perms['redistribute'] or recipient not in perms['audiences']: raise Refused('export refused')
        if authorize(copy(p), recipient, artifact_ref) is not True: raise Refused('delivery binding unverified')
        row = {'package':key,'digest':p['digest'],'recipient':recipient,'artifact_ref':artifact_ref,
               'states':{'delivered':artifact_ref,'acknowledged':None,'attached':None,'callable':None,'measured-useful':None}}
        self._deliveries.append(row)
        return copy(row)

    def record_delivery_state(self, index, state, receipt, verify):
        if state not in ('acknowledged','attached','callable','measured-useful'): raise Refused('delivery state')
        row = self._deliveries[index]; word(receipt)
        if self.package(row['package'])['local_status'] == 'stale': raise Refused('stale package')
        if verify(copy(row), state, receipt) is not True: raise Refused('state receipt unverified')
        if row['states'][state] is not None and row['states'][state] != receipt: raise Refused('immutable state receipt')
        row['states'][state] = receipt
        return copy(row)

    def checkpoint(self):
        body = {'schema':'omegalearn/checkpoint/1','events':self._events,'packages':self._packages,'stale':sorted(self._stale),'deliveries':self._deliveries}
        return copy(dict(body,digest=digest(body)))

    @classmethod
    def restore(cls, checkpoint):
        c = copy(checkpoint); exact(c, 'schema events packages stale deliveries digest')
        body = {k:v for k,v in c.items() if k != 'digest'}
        if c['schema'] != 'omegalearn/checkpoint/1' or digest(body) != c['digest']: raise Refused('corrupt checkpoint')
        obj = cls()
        for eid,e in c['events'].items():
            event_shape(e)
            if eid != e['id']: raise Refused('checkpoint event identity')
        obj._events = c['events']
        # Validate packages against intact sources before restoring staleness.
        pending = dict(c['packages'])
        while pending:
            ready = [(key,p) for key,p in pending.items() if p.get('rollback') is None or p['rollback'].get('id','')+'@'+p['rollback'].get('version','') in obj._packages]
            if not ready: raise Refused('checkpoint rollback cycle/missing predecessor')
            for key,p in ready:
                if obj.propose(p) != key: raise Refused('checkpoint package identity')
                del pending[key]
        if not set(c['stale']) <= set(obj._events): raise Refused('checkpoint stale identity')
        obj._stale = set(c['stale'])
        for row in c['deliveries']:
            exact(row,'package digest recipient artifact_ref states')
            p = obj._packages.get(row['package'])
            if not p or p['digest'] != row['digest']: raise Refused('checkpoint delivery binding')
            exact(row['states'],'delivered acknowledged attached callable measured-useful')
            if row['states']['delivered'] != row['artifact_ref']: raise Refused('checkpoint artifact binding')
        obj._deliveries = c['deliveries']
        return obj
