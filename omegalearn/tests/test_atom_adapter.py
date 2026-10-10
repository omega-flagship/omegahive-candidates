import pytest
from omegalearn import Ledger, Refused
from omegalearn.adapters import atom_resolver
from omegalearn.tests.test_foundation import event,resolver,package

def snapshot(e):
    return {'version':'0.1','owner':e['owner'],'scope':e['scope'],'revision':1,'records':[
        {'id':['ev',e['owner'],1],'statement':['Failure','missing-closer'],
         'source':{'owner':e['owner'],'subject':e['subject']['id'],'revision':1,'digest':e['subject']['digest']},
         'scope':e['scope'],'status':'simulated','stamp':[['ev',e['owner'],1]],'unknown':False,'truth':['stv',1,0.5]}]}

def prepared():
    e=event();e['subject']['revision']='1';e['evidence_refs']=['ev:source-owner:1'];return e,snapshot(e)

def test_actual_atom_validator_used_for_bound_source():
    e,s=prepared();l=Ledger();assert l.admit(e,lambda x:atom_resolver(x,s,resolver(x)))['new_evidence']
    s['records'][0]['unknown']=True
    with pytest.raises(ValueError):Ledger().admit(e,lambda x:atom_resolver(x,s,resolver(x)))

def test_atom_retraction_marks_local_package_stale():
    e,s=prepared();l=Ledger();l.admit(e,lambda x:atom_resolver(x,s,resolver(x)));key=l.propose(package(e))
    s['records'].append({'id':['ev',e['owner'],2],'statement':['Retracted',['ev',e['owner'],1],'correction',e['owner'],1],
        'source':{'owner':e['owner'],'subject':'withdrawal','revision':2,'digest':'b'*64},'scope':e['scope'],
        'status':'observed','stamp':[['ev',e['owner'],2]],'unknown':False,'truth':['stv',1,0.5]})
    with pytest.raises(Refused):atom_resolver(e,s,resolver(e))
    # Host authorizes invalidation separately; Atom data is not authority.
    l.invalidate(e['id'],lambda _:True)
    assert e['id'] in l.checkpoint()['stale']
    assert Ledger.restore(l.checkpoint()).package(key)['local_status']=='stale'


def test_unknown_atom_truth_stays_absent_through_intake():
    e,s=prepared();s['records'][0]['unknown']=True;s['records'][0].pop('truth')
    l=Ledger();l.admit(e,lambda x:atom_resolver(x,s,resolver(x)))
    assert 'truth' not in s['records'][0]
    assert 'truth' not in l.checkpoint()['events'][e['id']]


def test_query_page_requires_explicit_complete_lineage():
    from omegalearn.adapters import atom_query_resolver
    e,s=prepared()
    for flag in (False, None, 1, 'true'):
        with pytest.raises(Refused):atom_query_resolver(e,s,resolver(e),closure_complete=flag)
    assert Ledger().admit(e,lambda x:atom_query_resolver(x,s,resolver(x),closure_complete=True))['new_evidence']
    # A complete flag cannot override Atom's actual missing-premise check.
    s['records'][0].update(status='inferred', premises=[['ev',e['owner'],9]],rule=['demo'])
    with pytest.raises(ValueError):atom_query_resolver(e,s,resolver(e),closure_complete=True)
