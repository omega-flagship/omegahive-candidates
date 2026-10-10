"""L0 library: bounded job-local inference, D2-shaped proposals, no host writes."""
import contextlib, hashlib, importlib.util, io, json, math, os, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# PeTTa comes from PETTA_PATH; lib_pln.metta comes from the omegahive checkout that provides `hive`.
PETTA=Path(os.environ.get('PETTA_PATH') or ROOT/'.runtime/PeTTa')
def _pln_library():
    spec=importlib.util.find_spec('hive')
    return Path(spec.origin).resolve().parents[1]/'lib_pln.metta' if spec and spec.origin else ROOT/'lib_pln.metta'
TOKEN=re.compile(r'^[a-z][a-z0-9-]{0,63}$')

def symbol(value):
    if not isinstance(value,str) or not TOKEN.fullmatch(value):
        raise ValueError('Expected an inert lowercase symbol')
    return value

def number(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not 0<=value<=1:
        raise ValueError('Truth values must be supplied finite values in [0,1]')
    return value

def parse(text):
    tokens=re.findall(r'\(|\)|[^\s()]+',text)
    def node(index):
        if tokens[index]!='(': return tokens[index],index+1
        out=[];index+=1
        while index<len(tokens) and tokens[index]!=')':
            item,index=node(index);out.append(item)
        if index==len(tokens): raise ValueError('Unclosed native result')
        return out,index+1
    result,end=node(0)
    if end!=len(tokens):raise ValueError('Trailing native result')
    return result

def sentences(tree):
    if not isinstance(tree,list):return
    if len(tree)==3 and tree[0]=='Sentence':yield tree
    else:
        for item in tree:yield from sentences(item)

def pairs(tree):
    if not isinstance(tree,list):return
    if len(tree)==2 and isinstance(tree[0],list) and len(tree[0])==3 and tree[0][0]=='Inheritance' and isinstance(tree[1],list) and tree[1][0]=='stv':yield tree
    else:
        for item in tree:yield from pairs(item)

def validate(job):
    if not isinstance(job,dict):raise ValueError('Job must be an object')
    symbol(job['scope'])
    if not isinstance(job['premises'],list) or not 1<=len(job['premises'])<=24:raise ValueError('1..24 premises required')
    seen=set()
    for p in job['premises']:
        symbol(p['id']);symbol(p['subject']);symbol(p['object'])
        if p['id'] in seen:raise ValueError('Duplicate premise id')
        seen.add(p['id'])
        if p.get('relation')!='isa':raise ValueError('Only explicit isa/Inheritance translation supported')
        if p.get('status') not in ('observed','inferred','hypothetical','simulated','predicted','borrowed-prior','interventional'):raise ValueError('D2 status required')
        number(p['f']);number(p['c'])
        if not isinstance(p['stamp'],list) or not 1<=len(p['stamp'])<=24 or len(set(p['stamp']))!=len(p['stamp']):raise ValueError('Nonempty unique native evidence stamp required')
        for stamp in p['stamp']:symbol(stamp)
    for term,prior in job.get('priors',{}).items():
        symbol(term);symbol(prior['id'])
        if prior['id'] in seen:raise ValueError('Prior id collision')
        seen.add(prior['id'])
        a,b=prior['positive'],prior['total']
        if type(a)!=int or type(b)!=int or not 0<=a<=b or not 1<=b<=1000000:raise ValueError('Observed term counts required')
    for p in job['premises']:
        if not set(p.get('premises',[]))<=seen:raise ValueError('Unknown premise dependency')
    symbol(job.get('revision','r1'))
    return job

def stale_ids(job):
    stale=set(job.get('retracted',[]));known={p['id'] for p in job['premises']}|{p['id'] for p in job.get('priors',{}).values()}
    if not stale<=known:raise ValueError('Unknown retracted evidence id')
    while True:
        descendants={p['id'] for p in job['premises'] if set(p.get('premises',[]))&stale}
        new=stale|descendants
        if new==stale:return stale
        stale=new

def run(job,arm='combined'):
    """One bounded pair pass. Every engine runs in its own disposable process."""
    validate(job)
    if arm not in ('nal','pln','combined','typed-memory'):raise ValueError('Unknown arm')
    # Refuse oversized JSON before spawning; no raw MeTTa input is accepted.
    encoded=json.dumps(job)
    if len(encoded.encode())>32768:raise ValueError('Job too large')
    engines=['nal','pln'] if arm=='combined' else ([] if arm=='typed-memory' else [arm])
    results=[];diagnostics=[]
    for engine in engines:
        child=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',engine],input=encoded,text=True,capture_output=True,timeout=20,cwd=ROOT)
        if child.returncode:raise RuntimeError(child.stderr or 'Native worker failed')
        payload=json.loads(child.stdout.splitlines()[-1]);results+=payload['results'];diagnostics+=payload['diagnostics']
    return {'level':'L0','scope':job['scope'],'arm':arm,'results':results,'stale':sorted(stale_ids(job)),'diagnostics':diagnostics,'authority':'proposal-only','schema':'platform-D2-draft; Atom validator pending'}

def worker(job,engine):
    validate(job);stale=stale_ids(job)
    sys.path.insert(0,str(PETTA/'python'))
    from petta import PeTTa
    lib=PETTA/'lib/lib_nars.metta' if engine=='nal' else _pln_library()
    source=lib.read_text();library_digest=hashlib.sha256(source.encode()).hexdigest()
    version=hashlib.sha256((library_digest+hashlib.sha256(Path(__file__).read_bytes()).hexdigest()).encode()).hexdigest()
    m=PeTTa(verbose=False,petta_path=str(PETTA))
    diagnostics=[];results=[];dedup=set()
    m.process_metta_string('!(bind! &reason-job (new-space))')
    m.process_metta_string('!(bind! &reason-priors (new-space))')
    m.process_metta_string('!(bind! &reason-results (new-space))')
    if engine=='nal':m.load_metta_file(str(lib))
    else:
        stub='(= (STV $X) (stv (/ 1.0 10.0) 0.9))'
        if source.count(stub)!=1:raise ValueError('PLN prior binding changed; review adapter')
        m.process_metta_string(source.replace(stub,'(= (STV $X) (match &reason-priors (Prior $X $tv) $tv))'))
        for term,p in job.get('priors',{}).items():
            if p['id'] not in stale:
                # NAL count confidence k=1; this is derived from supplied counts.
                m.process_metta_string(f"!(add-atom &reason-priors (Prior {term} (stv {p['positive']/p['total']} {p['total']/(p['total']+1)})))")
    active=[p for p in job['premises'] if p['id'] not in stale]
    for p in active:
        relation='-->' if engine=='nal' else 'Inheritance'
        native=f"(({relation} {p['subject']} {p['object']}) (stv {p['f']} {p['c']}))"
        m.process_metta_string(f"!(add-atom &reason-job (Sentence {native} ({' '.join(p['stamp'])})))")
    for i,a in enumerate(active):
        for b in active[i+1:]:
            if set(a['stamp'])&set(b['stamp']):
                diagnostics.append({'engine':engine,'premises':[a['id'],b['id']],'refused':'overlapping-stamps'});continue
            ids=[a['id'],b['id']];terms=set([a['subject'],a['object'],b['subject'],b['object']])
            if engine=='pln':
                if any(t not in job.get('priors',{}) or job['priors'][t]['id'] in stale for t in terms):
                    diagnostics.append({'engine':engine,'premises':ids,'refused':'missing-active-term-priors'});continue
                ids+=sorted(job['priors'][t]['id'] for t in terms)
            def native(p,rel):return f"(({rel} {p['subject']} {p['object']}) (stv {p['f']} {p['c']}))"
            with contextlib.redirect_stdout(io.StringIO()):
                if engine=='nal':
                    expression=f"!(NARS.Derive ((Sentence {native(a,'-->')} ({' '.join(a['stamp'])}))) ((Sentence {native(b,'-->')} ({' '.join(b['stamp'])}))) 1 16 64)"
                else:expression=f"!(|~ {native(a,'Inheritance')} {native(b,'Inheritance')})"
                outputs=m.process_metta_string(expression)
            for output in outputs:
                tree=parse(output)
                candidates=[(s[1],s[2]) for s in sentences(tree)] if engine=='nal' else [(p,sorted(set(a['stamp']+b['stamp']))) for p in pairs(tree)]
                for pair,stamp in candidates:
                    if not isinstance(pair,list) or len(pair)!=2:
                        diagnostics.append({'engine':engine,'refused':'unsupported-native-form'});continue
                    statement,tv=pair
                    if not isinstance(statement,list) or len(statement)!=3 or statement[0]!=('-->' if engine=='nal' else 'Inheritance') or not all(isinstance(t,str) and TOKEN.fullmatch(t) for t in statement[1:]):
                        diagnostics.append({'engine':engine,'refused':'unsupported-native-form'});continue
                    rel,subject,obj=statement
                    if engine=='nal' and set(stamp)!=set(a['stamp']+b['stamp']):continue
                    symbol(subject);symbol(obj)
                    f,c=number(float(tv[1])),number(float(tv[2]))
                    if c==0:continue
                    key=(subject,obj,f,c,tuple(sorted(ids)),tuple(sorted(stamp)))
                    if key in dedup:continue
                    dedup.add(key)
                    material=json.dumps([job['scope'],job.get('revision','r1'),engine,version,key],sort_keys=True)
                    evidence='derived-'+hashlib.sha256(material.encode()).hexdigest()[:24]
                    rule='nars-derive' if engine=='nal' else 'pln-step'
                    envelope=[f'(Source {evidence} omegareason {evidence} {job.get("revision","r1")} "{hashlib.sha256(material.encode()).hexdigest()}")',f'(Status {evidence} inferred)',f'(Scope {evidence} {job["scope"]})',f'(Premises {evidence} ({" ".join(ids)}) (Rule {rule} "{version}"))']
                    for atom in envelope:
                        m.process_metta_string(f'!(add-atom &reason-results {atom})')
                    m.process_metta_string(f'!(add-atom &reason-results (Sentence (({rel} {subject} {obj}) (stv {f} {c})) ({" ".join(stamp)})))')
                    results.append({'id':evidence,'engine':engine,'status':'inferred','subject':subject,'relation':'isa','object':obj,'f':f,'c':c,'stamp':stamp,'stamp_origin':('native-nars' if engine=='nal' else 'wrapper-premise-union'),'premises':ids,'rule':rule,'version':version,'native_relation':rel,'atoms':[f'(Sentence (({rel} {subject} {obj}) (stv {f} {c})) ({" ".join(stamp)}))',*envelope]})
    if hashlib.sha256(lib.read_bytes()).hexdigest()!=library_digest:raise RuntimeError('Native source moved during job')
    return {'results':results,'diagnostics':diagnostics}

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker':
        print(json.dumps(worker(json.load(sys.stdin),sys.argv[2])))
    else:print(json.dumps(run(json.load(sys.stdin),sys.argv[1] if len(sys.argv)>1 else 'combined'),indent=2))
