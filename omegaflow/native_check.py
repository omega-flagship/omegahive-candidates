"""Disposable PeTTa proof of relational queries; never executes flow actions."""
import json
from pathlib import Path
from .examples.garden import garden
from .model import digest
from .symbolic import project, token


def run():
    from petta import PeTTa
    flow = garden(); d = digest(flow)
    q = lambda v: '"' + token(v) + '"'
    runtime = PeTTa(verbose=False)
    runtime.process_metta_string('\n'.join(project(flow)))
    queries = {
        'nary_members': f'!(match &self (OFRole {q(d)} {q("volunteers")} $role $position $member) $member)',
        'relation_about_relation': f'!(match &self (OFRole {q(d)} {q("attests")} {q("subject")} $position $member) $member)',
        'transition_edges': f'!(match &self (OFTransition {q(d)} $id $from $to) ($from $to))',
    }
    results = {name: runtime.process_metta_string(query) for name, query in queries.items()}
    expected = {
        'nary_members': ['"' + token(x) + '"' for x in ('visitor', 'garden', 'role')],
        'relation_about_relation': ['"' + token('volunteers') + '"'],
        'transition_edges': ['(' + q(a) + ' ' + q(b) + ')' for a, b in
                             (('visitor', 'signup'), ('signup', 'review'), ('review', 'welcome'))],
    }
    for name, values in expected.items():
        if sorted(results[name]) != sorted(values):
            raise RuntimeError('native relational query failed: ' + name)
    return {'flow_digest': d, 'queries': queries, 'results': results,
            'scope': 'real disposable PeTTa structural queries; no flow execution', 'execution_authorized': False}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
