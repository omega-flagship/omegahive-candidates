"""Consume OmegaAtom's canonical validator and lineage; return detached proposals."""
import copy,hashlib
from pathlib import Path
from omegaatom.envelope import validate,sidecars,lineage_state,digest,evidence_id
from .adapter import run

def infer_snapshot(snapshot,arm='combined'):
    snapshot=validate(snapshot)
    state={tuple(s['id']):s for s in lineage_state(snapshot)}
    records=sorted(snapshot['records'],key=lambda r:tuple(r['id']))
    names={tuple(r['id']):'e'+str(i+1) for i,r in enumerate(records)}
    inverse={value:list(key) for key,value in names.items()}
    premises=[];priors={};skipped=[]
    for r in records:
        if state[tuple(r['id'])]['retracted'] or state[tuple(r['id'])]['stale']:
            continue
        stmt=r['statement'];name=names[tuple(r['id'])]
        if len(stmt)==4 and stmt[0]=='TermCounts' and not r['unknown']:
            if stmt[1] in priors:raise ValueError('Multiple active term-count records require owner resolution')
            if r.get('premises'):raise ValueError('Derived term counts need an explicit count-model adapter')
            priors[stmt[1]]={'id':name,'positive':stmt[2],'total':stmt[3]}
        elif len(stmt)==3 and stmt[0]=='Inheritance' and not r['unknown']:
            premises.append({'id':name,'subject':stmt[1],'relation':'isa','object':stmt[2],
              'f':r['truth'][1],'c':r['truth'][2],'status':r['status'],
              'stamp':[names[tuple(e)] for e in r['stamp']],
              'premises':[names[tuple(e)] for e in r.get('premises',[])]})
        else:skipped.append(r['id'])
    if not premises:
        return {'snapshot':snapshot,'atoms':sidecars(snapshot),'native':None,'skipped':skipped,'authority':'proposal-only'}
    job={'scope':snapshot['scope'],'revision':'r'+str(snapshot['revision']),'premises':premises,'priors':priors}
    native=run(job,arm)
    result=copy.deepcopy(snapshot)
    next_sequence=max([r['id'][2] for r in records if r['id'][1]=='omegareason']+[0])+1
    bridge_version=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    existing={digest([r['statement'],r.get('premises'),r.get('rule'),r.get('truth')]):r for r in records if r['status']=='inferred'}
    for derived in native['results']:
        parent_ids=[inverse[e] for e in derived['premises']]
        statement=['Inheritance',derived['subject'],derived['object']]
        truth=['stv',derived['f'],derived['c']]
        rule=[derived['rule'],hashlib.sha256((derived['version']+bridge_version).encode()).hexdigest()]
        key=digest([statement,parent_ids,rule,truth])
        if key in existing:continue
        # Canonical envelope stamp includes ALL premises, including PLN prior evidence.
        index={tuple(r['id']):r for r in result['records']}
        stamp=sorted(set(tuple(e) for p in parent_ids for e in index[tuple(p)]['stamp']))
        identifier=['ev','omegareason',next_sequence];next_sequence+=1
        record={'id':identifier,'statement':statement,'source':{'owner':'omegareason','subject':'derived-'+key[:24],
                'revision':snapshot['revision'],'digest':key},'status':'inferred','scope':snapshot['scope'],
                'stamp':[list(e) for e in stamp],'unknown':False,'truth':truth,'premises':parent_ids,'rule':rule}
        result['records'].append(record);existing[key]=record
    result=validate(result)
    return {'snapshot':result,'atoms':sidecars(result),'native':native,'skipped':skipped,'authority':'proposal-only'}
