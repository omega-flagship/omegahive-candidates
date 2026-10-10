"""Offline repair subject for Bench's prompt-only worker; no custody authority."""
import copy
import hashlib
import time
from pathlib import Path
from .core import digest, Refused
from .repair import apply


class RepairExecutor:
    def __init__(self, content, training, mode, environment_pin):
        if mode not in ('FULL', 'SHAM', 'SEVERED', 'typed-memory'):
            raise Refused('unknown comparison mode')
        self._content = copy.deepcopy(content)
        self._training = tuple(tuple(pair) for pair in training)
        self._mode = mode
        self.environment_pin = environment_pin
        self.subject_pin = digest({
            'content': self._content, 'training': self._training, 'mode': mode,
            'sources': {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                        for name in ('bench_adapter.py', 'repair.py', 'core.py')},
            'controller': 'bounded-python-rule-interpreter/1'})

    def execute(self, request):
        # Binding failures refuse export through Bench's unknown-accounting path.
        if request['subject_pin'] != self.subject_pin or request['environment_pin'] != self.environment_pin:
            raise Refused('execution binding mismatch')
        started = time.monotonic()
        status, response = 'ok', None
        if started >= request['deadline_monotonic']:
            status = 'timeout'
        else:
            try:
                inp = request['input']
                if not isinstance(inp, dict) or set(inp) != {'text'} or not isinstance(inp['text'], str) or len(inp['text']) > 10000:
                    raise Refused('bounded text-only prompt required')
                computed = apply(self._content, inp['text']) if self._mode in ('FULL', 'SHAM') else None
                response = computed if self._mode == 'FULL' else dict(self._training).get(inp['text']) if self._mode == 'typed-memory' else None
            except Refused:
                status = 'failed'
        # Entire computation, including masked SHAM work, is metered. No model used.
        return dict(status=status, response=response,
                    usage=dict(cost=0, tokens=0, seconds=time.monotonic()-started, attempts=1),
                    floors={'bounded_response': int(response is None or (isinstance(response, str) and len(response) <= 10001))})


class PrerequisiteExecutor:
    """Learn component fixture, not a pinned Planner/controller subject.

    Trusted caller supplies a current package inspector. Baseline uses exact
    observed action/availability episodes; all labels remain development data.
    """
    def __init__(self, package, episodes, mode, environment_pin, inspect_package):
        if mode not in ('FULL','SHAM','SEVERED','typed-memory'):
            raise Refused('unknown comparison mode')
        self._package=copy.deepcopy(package)
        self._episodes=copy.deepcopy(episodes)
        self._inspect=inspect_package
        self._mode=mode
        self.environment_pin=environment_pin
        self.subject_pin=digest({'package':self._package,'episodes':self._episodes,'mode':mode,
            'controller':'learn-component-fixture/1',
            'sources':{name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                       for name in ('bench_adapter.py','prerequisites.py','core.py')}})

    def execute(self, request):
        from .prerequisites import check, ids
        if request['subject_pin'] != self.subject_pin or request['environment_pin'] != self.environment_pin:
            raise Refused('execution binding mismatch')
        started=time.monotonic();status='ok';response=None
        try:
            if started >= request['deadline_monotonic']:
                status='timeout'
            else:
                prompt=request['input']
                # Even masked/omitted components cannot consume withdrawn episodes.
                inspected=self._inspect(copy.deepcopy(self._package))
                if type(inspected) is not dict or inspected.pop('local_status',None) != 'proposed' or inspected != self._package:
                    raise Refused('stale or invalid source package')
                computed=check(self._package['content'],prompt) if self._mode in ('FULL','SHAM') else None
                if self._mode=='FULL':response=computed
                else:
                    if type(prompt) is not dict or set(prompt)!={'case','prerequisite_ids'} or type(prompt['case']) is not dict or set(prompt['case'])!={'actions','available'}:
                        raise Refused('approved prompt shape required')
                    vocabulary=ids(prompt['prerequisite_ids']);case=prompt['case']
                    actions,available=ids(case['actions']),ids(case['available'])
                    if not available <= vocabulary:raise Refused('availability outside vocabulary')
                    matched=[e for e in self._episodes if actions=={e['action']} and available==set(e['available'])]
                    response=sorted(matched[0]['missing']) if matched else []
                    if not set(response)<=vocabulary:raise Refused('baseline outside vocabulary')
        except Refused:
            status='failed';response=None
        bounded=type(response) is list and len(response)<=128 and all(type(x) is str for x in response)
        return dict(status=status,response=response,
            usage=dict(cost=0,tokens=0,seconds=time.monotonic()-started,attempts=1),
            floors={'canonical_response':int(bounded and response==sorted(set(response)))})
