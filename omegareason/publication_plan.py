"""Pure r2 S1 batch preparation. Host custody, allocation and commit are external."""
from omegaatom.envelope import validate,digest,format_evidence_ref

def prepare_batch(base,candidate):
    base,candidate=validate(base),validate(candidate)
    if base['scope']!=candidate['scope'] or base['owner']!=candidate['owner'] or base['revision']!=candidate['revision']:
        raise ValueError('Candidate must extend exactly the supplied frozen base')
    before={tuple(r['id']):r for r in base['records']}
    after={tuple(r['id']):r for r in candidate['records']}
    if not before.keys()<=after.keys() or any(after[k]!=r for k,r in before.items()):
        raise ValueError('Base history was removed or rewritten')
    facts=[]
    for record in candidate['records']:
        if tuple(record['id']) in before:continue
        # Local ids are correlation labels, NEVER requested host evidence identities.
        payload={'statement':record['statement'],'source_reference':record['source'],'status':record['status'],
                 'unknown':record['unknown'],'scope':record['scope'],
                 'premise_refs':[format_evidence_ref(e) for e in record.get('premises',[])]}
        if record.get('rule'):payload['rule']=record['rule']
        if not record['unknown']:payload.update(f=record['truth'][1],c=record['truth'][2])
        pin=digest(payload)
        facts.append({'local_ref':format_evidence_ref(record['id']), 'idempotency_key':'reason-'+pin,
                      'prepared_payload_digest':pin,'payload':payload})
    return {'schema':'reason-s1-preparation-r2','base_revision':base['revision'],'base_digest':digest(base),
            'scope':base['scope'],'facts':facts,'batch_key':'reason-batch-'+digest([f['prepared_payload_digest'] for f in facts]),
            'authority':'none','requires':['host-authenticated source custody and admitted premise closure',
               'host-issued ids/stamps and local-ref rebinding before Atom validation',
               'all-or-nothing host transaction','durable idempotency key/final-payload digest replay'],
            'wire_status':'preallocation plan only; exact S1 request schema is not frozen'}
