"""Independent synthetic outcome evaluator, not a Lab or native-mind receipt."""
from .repair import learn, apply, missing_closer

def run():
    training=[('(a b','(a b)'),('(x (y z)','(x (y z))')]
    content=learn(training)
    # Fixed unseen tasks and expected outputs are kept out of learner construction.
    tasks=[('(fresh k','(fresh k)'),('(new (nested 7)','(new (nested 7))'),
           ('(say "paren ( inside"','(say "paren ( inside")'),
           ('(two (missing',None),('(quote "open',None),('(already valid)',None),('extra)',None)]
    arms={}
    for arm in ('FULL','SHAM','SEVERED','typed-memory'):
        rows=[]
        for text,expected in tasks:
            computed=apply(content,text) if arm in ('FULL','SHAM') else None
            output=computed if arm=='FULL' else dict(training).get(text) if arm=='typed-memory' else None
            correct=output==expected and (output is None or missing_closer(output)==0)
            rows.append({'input':text,'expected':expected,'output':output,'correct':correct})
        arms[arm]={'correct':sum(r['correct'] for r in rows),'tasks':len(rows),'model_calls':0,'rows':rows}
    return {'level':'L0','domain':'synthetic delimiter repair with abstention',
            'claims':'offline transfer under explicit rule interpreter; no semantic repair/native mind/host execution',
            'deferred_baselines':['NACE-only','PC versus equal-topology backprop'], 'arms':arms,'skill':content}
