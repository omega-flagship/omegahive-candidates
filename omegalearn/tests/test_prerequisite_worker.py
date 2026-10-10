import pytest as _pytest
_pytest.importorskip('omegabench.planner_adapter', reason='needs the separate omegabench package on PYTHONPATH')
import json
from pathlib import Path
from omegalearn import Ledger
from omegalearn.bench_adapter import PrerequisiteExecutor
from omegalearn.tests.test_foundation import resolver
from omegabench.demo import example
from omegabench.protocol import digest
from omegabench.planner_adapter import case
from omegabench.worker import run,evaluator_pin


def test_shared_worker_component_and_accounted_withdrawal():
    root=Path(__file__).resolve().parent/'fixtures'
    source=json.loads((root/'PREREQUISITE_SOURCE_DEVELOPMENT.json').read_text())
    package=json.loads((root/'PREREQUISITE_PACKAGE_DEVELOPMENT.json').read_text())
    ledger=Ledger();ledger.admit(source['event'],resolver);key=ledger.propose(package)
    inspect=lambda _:ledger.package(key)
    env=digest('development-component-only-no-planner-capture')
    prompts=[([],['approval','review']),(['approval'],['review']),(['review'],['approval']),(['approval','review'],[])]
    pack=[case(f'c{i}','availability',{'actions':['publish'],'available':available},['approval','review'],missing)
          for i,(available,missing) in enumerate(prompts)]
    scores={}
    for mode in ('FULL','SHAM','SEVERED'):
        baseline=PrerequisiteExecutor(package,source['episodes'],'typed-memory',env,inspect)
        candidate=PrerequisiteExecutor(package,source['episodes'],mode,env,inspect)
        r,_,_=example();r.update(baseline_pin=baseline.subject_pin,candidate_pin=candidate.subject_pin,
            evaluator_pin=evaluator_pin(),dataset_pin=digest(pack),environment_pin=env,
            task_ids=[t['id'] for t in pack],task_families={t['id']:t['family'] for t in pack},
            limits={'cost':0,'tokens':0,'seconds':10,'attempts':4},floors={'canonical_response':1})
        export,audit=run(r,pack,{'baseline':baseline,'candidate':candidate})
        scores[mode]=sum(row['score'] for row in export['candidate'])
        assert sum(row['score'] for row in export['baseline'])==3
        assert len(export['candidate'])==4 and all(row['attempts']==1 for row in export['candidate'])
        assert not audit['adoption_authorized']
    assert scores=={'FULL':4,'SHAM':3,'SEVERED':3}
    ledger.invalidate(source['event']['id'],lambda _:True)
    export,_=run(r,pack,{'baseline':baseline,'candidate':candidate})
    assert all(row['status']=='failed' and row['attempts']==1 and row['score']==0 for arm in ('baseline','candidate') for row in export[arm])
