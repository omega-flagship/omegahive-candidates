"""Synthetic L0 test against the real OmegaAtom candidate API."""
import copy,json,os,subprocess,sys,tempfile
from pathlib import Path
from omegaatom.envelope import validate,dumps,loads,lineage_state,digest
from .atom_bridge import infer_snapshot
ROOT=Path(__file__).resolve().parents[1]

def source(seq,statement,truth=None):
    r={'id':['ev','lab',seq],'statement':statement,'source':{'owner':'lab','subject':'record-'+str(seq),'revision':1,'digest':digest(statement)},
       'status':'simulated','scope':'synthetic-atom','stamp':[['ev','lab',seq]],'unknown':truth is None}
    if truth is not None:r['truth']=truth
    return r

def execute():
    base={'version':'0.1','owner':'lab','scope':'synthetic-atom','revision':1,'records':[
      source(1,['Inheritance','alpha','beta'],['stv',.8,.7]),source(2,['Inheritance','beta','gamma'],['stv',.8,.7]),
      source(3,['Inheritance','unrelated','other'],['stv',.8,.7]),
      *[source(i+4,['TermCounts',term,50,100],['stv',.5,100/101]) for i,term in enumerate(['alpha','beta','gamma','unrelated','other'])]]}
    outputs={arm:infer_snapshot(base,arm) for arm in ['nal','pln','combined','typed-memory']}
    derived=lambda out:[r for r in out['snapshot']['records'] if r['status']=='inferred']
    checks={'all-arms-canonical-validation':all(validate(o['snapshot']) for o in outputs.values()),
      'both-engines-derived':all(derived(outputs[arm]) for arm in ['nal','pln','combined']),
      'all-atoms-inert-sidecars':all(any(a[0]=='Premises' for a in outputs[arm]['atoms']) for arm in ['nal','pln','combined'])}
    unknown_counts=copy.deepcopy(base)
    for r in unknown_counts['records']:
        if r['statement'][0]=='TermCounts':r['unknown']=True;r.pop('truth',None)
    checks['unknown-counts-refused']=not infer_snapshot(unknown_counts,'pln')['native']['results']
    retained=outputs['combined']['snapshot']
    event=source(20,['Retracted',['ev','lab',1],'synthetic-correction','lab',1],['stv',1,.5]);event['status']='observed'
    withdrawn=copy.deepcopy(retained);withdrawn['records'].append(event);withdrawn['revision']=2
    state=lineage_state(withdrawn)
    stale={tuple(s['id']) for s in state if s['stale']}
    expected={tuple(r['id']) for r in derived(outputs['combined']) if ['ev','lab',1] in r['premises']}
    checks['atom-exact-descendant-staleness']=stale==expected and bool(stale)
    after=infer_snapshot(withdrawn)
    checks['archive-retained']=len(after['snapshot']['records'])==len(withdrawn['records'])
    checks['no-rederivation-from-stale-input']=not after['native']['results']
    corrected=copy.deepcopy(withdrawn);corrected['revision']=3
    corrected['records'].append(source(21,['Inheritance','alpha','beta'],['stv',.8,.7]))
    new=infer_snapshot(corrected)
    fresh=[r for r in new['snapshot']['records'] if r not in corrected['records']]
    checks['new-evidence-rederives']=bool(fresh) and all(['ev','lab',1] not in r['premises'] for r in fresh)
    checks['prior-evidence-in-canonical-stamp']=all(set(map(tuple,r['stamp']))==set(tuple(e) for p in r['premises'] for e in next(x for x in new['snapshot']['records'] if x['id']==p)['stamp']) for r in fresh)
    with tempfile.TemporaryDirectory(prefix='reason-atom-restore-') as folder:
        path=Path(folder)/'snapshot.json';path.write_text(dumps(new['snapshot']))
        script='import json,sys;from omegaatom.envelope import loads;from omegareason.atom_bridge import infer_snapshot; print(json.dumps(infer_snapshot(loads(sys.stdin.read()))))'
        child=subprocess.run([sys.executable,'-c',script],input=path.read_text(),text=True,capture_output=True,cwd=ROOT,timeout=45)
        restored=json.loads(child.stdout) if child.returncode==0 else {}
        checks['canonical-restart-and-idempotence']=restored.get('snapshot')==new['snapshot']
    report={'level':'L0','scope':'real OmegaAtom pure validator with synthetic source records; detached proposals only','checks':{k:bool(v) for k,v in checks.items()},'passed':all(checks.values()),'arms':{k:v['snapshot'] for k,v in outputs.items()},'retraction_state':state,'corrected_snapshot':new['snapshot']}
    out=Path(os.environ.get('OMEGAREASON_RECEIPT_DIR') or ROOT/'omegareason-receipts');out.mkdir(parents=True,exist_ok=True)
    (out/'ATOM_BRIDGE_QUALIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'level':'L0','checks':report['checks'],'passed':report['passed']}));return report['passed']
if __name__=='__main__':sys.exit(0 if execute() else 1)
