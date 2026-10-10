"""Reason proposal export for existing exact typed review requests; no publication."""
import json
from omegaatom.envelope import validate,canonical,digest,format_evidence_ref,parse_evidence_ref,lineage_state

def seal(snapshot):
    snapshot=validate(snapshot)
    report={'schema':'omegareason-review-0.1','snapshot':snapshot,'snapshot_digest':digest(snapshot),
            'evidence_refs':[format_evidence_ref(r['id']) for r in snapshot['records']],
            'lineage_state':lineage_state(snapshot),'authority':'proposal-only'}
    body=canonical(report)
    if len(body.encode())>200000:raise ValueError('Review export exceeds bounded artifact size')
    return body

def open_revision(revision,subject):
    """Consume only an authorized host read; recheck content identity locally too."""
    from hive.core.collab import digest as wire_digest
    if revision['artifact_id']!=subject['artifact_id'] or revision['n']!=subject['revision']:
        raise ValueError('Wrong retained revision')
    if revision['digest']!=subject['digest'] or wire_digest(revision['body'])!=subject['digest']:
        raise ValueError('Artifact digest mismatch')
    body=revision['body']
    if len(body.encode())>200000:raise ValueError('Review export exceeds bound')
    def pairs(items):
        out={}
        for key,value in items:
            if key in out:raise ValueError('Duplicate export key')
            out[key]=value
        return out
    report=json.loads(body,object_pairs_hook=pairs)
    if set(report)!={'schema','snapshot','snapshot_digest','evidence_refs','lineage_state','authority'} or report['schema']!='omegareason-review-0.1' or report['authority']!='proposal-only':raise ValueError('Invalid Reason export')
    snapshot=validate(report['snapshot'])
    expected=[format_evidence_ref(r['id']) for r in snapshot['records']]
    if report['evidence_refs']!=expected or [parse_evidence_ref(e) for e in expected]!=[r['id'] for r in snapshot['records']]:raise ValueError('Evidence refs mismatch')
    if digest(snapshot)!=report['snapshot_digest'] or lineage_state(snapshot)!=report['lineage_state']:raise ValueError('Snapshot or state mismatch')
    return report

def review_request(from_goal,to_swarm,subject):
    """Payload for /api/agent/requests, not a new transport or grant."""
    if set(subject)!={'artifact_id','revision','digest'}:raise ValueError('Exact artifact revision binding required')
    return {'kind':'review','title':'Review Reason lineage proposal','from_goal':from_goal,'to_swarm':to_swarm,
            'budget_usd':0,'subject':dict(subject),
            'constraints':{'mandates':[{'id':'reason-lineage','version':'1'}]},'context_refs':[]}
