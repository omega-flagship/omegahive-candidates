import pytest as _pytest
_pytest.importorskip('omegaplanner.learning', reason='needs the separate omegaplanner package on PYTHONPATH')
import pytest
from omegalearn import Ledger, Refused, digest
from omegalearn.prerequisites import learn, check
from omegalearn.tests.test_foundation import event, resolver, package
from omegaplanner.learning import from_learn_ledger


def episodes():
    return [dict(action='publish', required=['review','approval'], available=['review'], missing=['approval']),
            dict(action='publish', required=['review','approval'], available=[], missing=['review','approval'])]


def test_transfer_new_availability_and_multiple_actions():
    rows=episodes()+[dict(action='deploy', required=['tests'], available=[], missing=['tests'])]
    c=learn(rows,['ev:source-owner:1'])
    prompt={'case':{'actions':['publish','deploy'], 'available':['approval']}, 'prerequisite_ids':['approval','review','tests']}
    assert check(c,prompt)==['review','tests']
    prompt['case']['available']=['approval','review','tests']
    assert check(c,prompt)==[]


@pytest.mark.parametrize('change',['conflict','wrong-outcome','unseen','unknown-vocabulary','arbitrary-rule'])
def test_refusal_boundaries(change):
    rows=episodes()
    if change=='conflict':rows[1]['required']=['review'];rows[1]['missing']=['review']
    if change=='wrong-outcome':rows[1]['missing']=[]
    if change in ('conflict','wrong-outcome'):
        with pytest.raises(Refused):learn(rows,['ev:source-owner:1'])
        return
    c=learn(rows,['ev:source-owner:1'])
    p={'case':{'actions':['publish'],'available':[]},'prerequisite_ids':['approval','review']}
    if change=='unseen':p['case']['actions']=['unknown']
    if change=='unknown-vocabulary':p['prerequisite_ids']=['review']
    if change=='arbitrary-rule':c['rules']=['!(delete-all)']
    with pytest.raises(Refused):check(c,p)


def test_real_package_planner_receipt_and_source_withdrawal():
    ledger=Ledger(); e=event();e['evidence_refs']=['ev:source-owner:1'];e['payload']={'kind':'experience','data':{'episodes':episodes()}}
    consumer=from_learn_ledger(ledger,resolver);ledger.admit(e,resolver)
    p=package(e);p.update(id='prerequisite-check',content=learn(episodes(),e['evidence_refs']),evaluation_refs=[],runtime={'requires':['omegalearn:0.1'],'entrypoint':'prerequisites.check'})
    p['digest']=digest({k:v for k,v in p.items() if k!='digest'})
    row=consumer.receive_candidate(p)
    assert row['recipient_receipt'] and not row['execution_authorized'] and not row['attached']
    ledger.invalidate(e['id'],lambda _:True)
    with pytest.raises((Refused, __import__("omegaplanner.protocol", fromlist=["Refused"]).Refused)):consumer.candidate(p['id'],p['version'])
    assert Ledger.restore(ledger.checkpoint()).package('prerequisite-check@1')['local_status']=='stale'
