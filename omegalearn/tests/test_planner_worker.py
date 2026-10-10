import pytest as _pytest
_pytest.importorskip('omegaplanner.bench_subject', reason='needs the separate omegaplanner package on PYTHONPATH')
_pytest.importorskip('omegabench.planner_adapter', reason='needs the separate omegabench package on PYTHONPATH')
import json
from pathlib import Path
from omegalearn import Ledger
from omegaplanner.bench_subject import PlannerExecutor
from omegaplanner.learning import from_learn_ledger
from omegalearn.tests.test_foundation import resolver
from omegabench.demo import example
from omegabench.protocol import digest
from omegabench.planner_adapter import case
from omegabench.worker import run,evaluator_pin


def test_shared_worker_planner_consumer_and_accounted_withdrawal():
    root=Path(__file__).resolve().parent/'fixtures'
    source=json.loads((root/'PREREQUISITE_SOURCE_DEVELOPMENT.json').read_text())
    package=json.loads((root/'PREREQUISITE_PACKAGE_DEVELOPMENT.json').read_text())
    ledger=Ledger();ledger.admit(source['event'],resolver);key=ledger.propose(package)
    consumer=from_learn_ledger(ledger,resolver);consumer.receive_candidate(package)
    config={"baseline":"unchanged-exact-episode","provider":"none"}
    env=digest('development-component-only-no-planner-capture')
    prompts=[([],['approval','review']),(['approval'],['review']),(['review'],['approval']),(['approval','review'],[])]
    pack=[case(f'c{i}','availability',{'actions':['publish'],'available':available},['approval','review'],missing)
          for i,(available,missing) in enumerate(prompts)]
    scores={}
    for mode in ('FULL','SHAM','SEVERED'):
        baseline=PlannerExecutor(consumer,package,source['episodes'],'typed-memory',env,config)
        candidate=PlannerExecutor(consumer,package,source['episodes'],mode,env,config)
        r,_,_=example();r.update(baseline_pin=baseline.subject_pin,candidate_pin=candidate.subject_pin,
            evaluator_pin=evaluator_pin(),dataset_pin=digest(pack),environment_pin=env,
            task_ids=[t['id'] for t in pack],task_families={t['id']:t['family'] for t in pack},
            limits={'cost':0,'tokens':0,'seconds':10,'attempts':4},floors={'canonical_response':1})
        export,audit=run(r,pack,{'baseline':baseline,'candidate':candidate})
        scores[mode]=sum(row['score'] for row in export['candidate'])
        assert sum(row['score'] for row in export['baseline'])==3
        assert len(export['candidate'])==4 and all(row['attempts']==1 for row in export['candidate'])
        assert not audit['adoption_authorized']
        captures=candidate.captures()
        assert len(captures)==4
        assert all(c['local_plan'] is not None and c['plan_artifact'] is None and c['capture_receipt'] is None and not c['capability_acceptance_ready'] for c in captures)
        if mode=='FULL':
            assert captures[1]['local_plan']['body']['steps'][-1]['depends_on']==['prereq-review']
    assert scores=={'FULL':4,'SHAM':3,'SEVERED':3}
    ledger.invalidate(source['event']['id'],lambda _:True)
    export,_=run(r,pack,{'baseline':baseline,'candidate':candidate})
    assert all(row['status']=='failed' and row['attempts']==1 and row['score']==0 for arm in ('baseline','candidate') for row in export[arm])
