import copy
import pytest
from omegaflow.examples.garden import garden
from omegaflow.admission import prepare


def executable_shape():
    f=garden()
    elements={e['id']:e for e in f['elements']}
    # Invented, descriptive adoption; not a host-authorized artifact.
    for e in f['elements']: e['meta']['revision_state']='adopted'
    elements['submitted']['type']='run.start'
    elements['accepted']['type']='goal.done';elements['accepted']['props']['source_transition']='t0'
    event=copy.deepcopy(elements['accepted']);event['id']='review-done';event['props']['source_transition']='t1';f['elements'].append(event)
    elements['t1']['trigger']='accepted';elements['t2']['trigger']='review-done'
    elements['t2']['props']['requires_approval']=False
    return f


def test_preflight_cannot_authorize_even_valid_shape():
    r=prepare(executable_shape())
    assert r['structurally_eligible'] and not r['execution_authorized']
    assert r['host_requirements']


def test_display_example_is_refused_as_executable():
    r=prepare(garden())
    assert not r['structurally_eligible']
    assert {'unsupported-trigger','transition-not-adopted','approval-execution-unqualified'} <= {e['code'] for e in r['findings']}


@pytest.mark.parametrize('case,code',[
    ('action','unsupported-action'),('source','missing-run-local-source'),
    ('source-state','source-state-mismatch'),('source-action','source-action-mismatch'),
    ('loop','cycle-execution-unqualified'),('join','join-execution-unqualified'),
    ('guards','guard-execution-unqualified'),('unreachable','unreachable-transition')])
def test_unsupported_or_ambiguous_execution_refused(case,code):
    f=executable_shape();es={e['id']:e for e in f['elements']}
    if case=='action':es['t1']['action']['kind']='program_action'
    if case=='source':es['accepted']['props']['source_transition']='unknown'
    if case=='source-state':es['accepted']['props']['source_transition']='t2'
    if case=='source-action':es['t0']['action']['kind']='message'
    if case=='loop':es['t2']['to']='visitor'
    if case=='join':es['t2']['to']='signup'
    if case=='guards':
        c=copy.deepcopy(es['visitor']);c.update(id='c',kind='constraint',predicate='all-present',members=['visitor']);del c['type'];del c['ref'];f['elements'].append(c);es['t1']['guards']=['c']
    if case=='unreachable':es['t1']['from']='person'
    assert code in {e['code'] for e in prepare(f)['findings']}
