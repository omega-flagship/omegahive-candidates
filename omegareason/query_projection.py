"""Consume Atom's closed page groups; no query endpoint, grants or cursors."""
import copy
from omegaatom.envelope import validate,evidence_id,digest
from omegaatom.projection import project_pages
from .atom_bridge import infer_snapshot

def join_pages(pages):
    """Merge one granted projection, not scopes; duplicate ancestors must agree.

    Closure markers are a host assertion. This validates structure, not custody
    or whether an untrusted sender concealed a withdrawal from its history.
    """
    if not isinstance(pages,list) or not 1<=len(pages)<=1000:raise ValueError('Bounded complete page list required')
    merged=None;records={};binding=None
    for position,page in enumerate(pages):
        if not isinstance(page,dict) or set(page)!={'snapshot','closure_complete','result_complete'}:raise ValueError('Atom page fields mismatch')
        if page['closure_complete'] is not True or page['result_complete'] is not (position==len(pages)-1):raise ValueError('Partial or reordered result groups refused')
        snapshot=validate(page['snapshot'])
        if len(snapshot['records'])>200:raise ValueError('Host query page exceeds 200 records')
        current=(snapshot['owner'],snapshot['scope'],snapshot['revision'])
        if binding is not None and current!=binding:raise ValueError('Mixed owner, scope or revision pages')
        binding=current
        if merged is None:merged=copy.deepcopy(snapshot)
        for record in snapshot['records']:
            key=evidence_id(record['id'])
            if key in records and records[key]!=record:raise ValueError('Conflicting repeated evidence across pages')
            records[key]=copy.deepcopy(record)
    merged['records']=[records[key] for key in sorted(records)]
    return validate(merged)

def project_and_reason(snapshot,roots,arm='combined',record_limit=200):
    """Owner-local reference route: host must authorize and supply the snapshot.

    Atom projects all groups first, including every control. Only after every
    group succeeds does bounded inference start; overflow yields no partial work.
    """
    snapshot=validate(snapshot)
    pages=project_pages(snapshot,roots,record_limit=record_limit)
    joined=join_pages(pages)
    result=infer_snapshot(joined,arm)
    return {'pages':pages,'projection_digest':digest(joined),'reason':result,
            'authority':'proposal-only','access':'caller supplies owner-local or host-authorized data; no grant minted'}
