"""Revision-bound consumer for the existing Scientist/goal route; no scheduler or I/O."""
import copy,datetime
from hive.core.goals import binding_digest,MAX_RESULT_DATA_BYTES
from hive.core.shares import exhibit_digest
from omegaatom.envelope import validate,loads,dumps,digest,sidecars
from .atom_bridge import infer_snapshot

class Refused(ValueError):pass

def check(condition,reason):
    if not condition:raise Refused(reason)

def active(goal,agent_id):
    check(goal.get('status')=='claimed','goal not claimed or no longer active')
    check(goal.get('claimed_by')==agent_id,'worker is not the claimer')
    check(goal.get('assignee') in (None,agent_id),'wrong assignee')
    now=datetime.datetime.now(datetime.timezone.utc)
    for key in ('deadline_at','lease_until'):
        if goal.get(key):
            check(datetime.datetime.fromisoformat(goal[key].replace('Z','+00:00'))>now,key+' expired')

def mark_advice(snapshot,fresh_ids):
    """Ordinary truthless D2 statements, not a new sidecar schema or grants."""
    snapshot=copy.deepcopy(snapshot)
    index={tuple(r['id']):r for r in snapshot['records']}
    seq=max([r['id'][2] for r in snapshot['records'] if r['id'][1]=='omegareason']+[0])+1
    for target in fresh_ids:
        parent=index[tuple(target)]
        for head,state in [('AdmissionState','proposed'),('Restriction','proposal-only')]:
            statement=[head,target,state];key=digest(statement)
            record={'id':['ev','omegareason',seq],'statement':statement,'source':{'owner':'omegareason',
                'subject':head.lower()+'-'+key[:24],'revision':snapshot['revision'],'digest':key},
                'status':'inferred','scope':snapshot['scope'],'stamp':parent['stamp'],'unknown':True,
                'premises':[target],'rule':['reason-advice-v1','0.1.0']}
            snapshot['records'].append(record);seq+=1
    return validate(snapshot)

def prepare(goal,exhibit,agent_id,arm='combined'):
    active(goal,agent_id)
    binding=goal['binding'];echo=binding_digest(binding)
    check(goal.get('binding_digest')==echo,'binding digest mismatch')
    check(exhibit.get('kind')=='exhibit' and exhibit.get('complete') is True and exhibit.get('offset')==0,'incomplete or non-exhibit snapshot')
    check(exhibit.get('share_id') in binding.get('share_ids',[]),'unbound share')
    shown=exhibit_digest(exhibit['title'],exhibit['body'],exhibit['atoms'])
    check(shown==exhibit.get('digest')==binding.get('snapshot_digest'),'exhibit digest mismatch')
    source=loads(exhibit['body'])
    check(source['revision']==binding.get('base_revision'),'snapshot revision mismatch')
    check(digest(source)==binding.get('envelope_digest'),'envelope digest mismatch')
    analysis=infer_snapshot(source,arm)
    old={tuple(r['id']) for r in source['records']}
    fresh=[r['id'] for r in analysis['snapshot']['records'] if tuple(r['id']) not in old]
    proposal=mark_advice(analysis['snapshot'],fresh)
    data={'binding_digest':echo,'proposal':{'snapshot':proposal,'arm':arm,'base_digest':digest(source)}}
    import json
    check(len(json.dumps(data).encode())<=MAX_RESULT_DATA_BYTES,'result exceeds host data bound')
    return {'goal_id':goal['id'],'agent_id':agent_id,'binding_digest':echo,'base_revision':source['revision'],
            'base_digest':digest(source),'data':data,'result':'Bounded reasoning proposal; awaiting owner review.'}

def finalize(prepared,fresh_goal,current_snapshot):
    """Caller re-reads host goal and owner snapshot immediately before submission."""
    active(fresh_goal,prepared['agent_id'])
    check(fresh_goal['id']==prepared['goal_id'],'goal changed')
    check(binding_digest(fresh_goal['binding'])==fresh_goal.get('binding_digest')==prepared['binding_digest'],'binding changed')
    current=validate(current_snapshot)
    check(current['revision']==prepared['base_revision'] and digest(current)==prepared['base_digest'],'owner snapshot changed')
    return {'status':'done','result':prepared['result'],'data':copy.deepcopy(prepared['data'])}
