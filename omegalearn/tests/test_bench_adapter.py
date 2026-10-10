import pytest
from omegalearn.bench_adapter import RepairExecutor
from omegalearn.repair import learn
from omegalearn.core import Refused
from omegabench.demo import example
from omegabench.protocol import digest
from omegabench.worker import run, evaluator_pin


def test_worker_prompt_only_repair_comparisons():
    training = [('(a b', '(a b)'), ('(x (y z)', '(x (y z))')]
    content = learn(training)
    texts = [('(unseen', '(unseen)'), ('(nested (new)', '(nested (new))'),
             ('(say "("', '(say "(")'), ('(two (open', None),
             ('(quote "', None), ('(valid)', None), ('extra)', None)]
    pack = [dict(id=f'case-{i}', family=f'family-{i}', input={'text':text}, expected=answer)
            for i, (text, answer) in enumerate(texts)]
    environment = digest('public-development-offline-python-no-isolation')
    scores = {}
    for mode in ('FULL', 'SHAM', 'SEVERED', 'typed-memory'):
        baseline = RepairExecutor(content, training, 'typed-memory', environment)
        candidate = RepairExecutor(content, training, mode, environment)
        r, _, _ = example()
        r.update(baseline_pin=baseline.subject_pin, candidate_pin=candidate.subject_pin,
                 evaluator_pin=evaluator_pin(), dataset_pin=digest(pack), environment_pin=environment,
                 task_ids=[t['id'] for t in pack], task_families={t['id']:t['family'] for t in pack},
                 limits={'cost':0, 'tokens':0, 'seconds':10, 'attempts':7}, floors={'bounded_response':1})
        # Identical typed-memory arms are a control, not a registered improvement.
        if mode == 'typed-memory':
            with pytest.raises(ValueError): run(r, pack, {'baseline':baseline, 'candidate':candidate})
            continue
        export, audit = run(r, pack, {'baseline':baseline, 'candidate':candidate})
        scores[mode] = sum(row['score'] for row in export['candidate'])
        assert sum(row['score'] for row in export['baseline']) == 4
        assert all(row['attempts'] == 1 and row['seconds'] > 0 for row in export['candidate'])
        assert audit['oracle_custody'] == 'unverified' and not audit['adoption_authorized']
    assert scores == {'FULL':7, 'SHAM':4, 'SEVERED':4}


def test_pin_changes_with_behavior_and_binding_refuses():
    content = learn([('(a', '(a)'), ('(b', '(b)')])
    full = RepairExecutor(content, [], 'FULL', 'env')
    sham = RepairExecutor(content, [], 'SHAM', 'env')
    assert full.subject_pin != sham.subject_pin
    with pytest.raises(Refused): full.execute({'subject_pin':sham.subject_pin, 'environment_pin':'env'})
