import copy
import pytest
from omegaflow import canonical, digest, validate, revision, check_structure, project, recover
from omegaflow.examples.garden import garden
from omegaflow.symbolic import atom


def test_round_trip_nary_and_relation_about_relation():
    f = garden()
    atoms = project(f)
    assert canonical(recover(list(reversed(atoms)))) == canonical(f)
    assert project(recover(atoms)) == atoms
    assert sum(a.startswith('(OFRole ') for a in atoms) == 5


def test_hostile_unicode_and_pinned_subflow():
    f = garden()
    f['elements'][0]['props'] = {'label': '你好 🌱 " ) !(evil &self)\n\\', 'nested': [None, False, 1.25]}
    e = copy.deepcopy(f['elements'][0]); e.update(id='sub', kind='subflow', flow_id='other', revision_digest='a'*64)
    del e['type']; del e['ref']; f['elements'].append(e)
    assert recover(project(f)) == f
    assert 'evil' not in '\n'.join(project(f))


def test_layout_is_not_semantic_revision():
    f = garden()
    a = revision(f, {'visitor': {'x': 0, 'y': 1}})
    b = revision(f, {'visitor': {'x': 100, 'y': -4}})
    assert a['digest'] == b['digest']
    f['elements'][9]['action']['params']['step'] = 'changed'
    assert revision(f)['digest'] != a['digest']


@pytest.mark.parametrize('mutation', ['duplicate-id', 'dangling-role', 'wrong-event', 'unpinned', 'nan', 'code-constraint'])
def test_invalid_model_refused(mutation):
    f = garden()
    if mutation == 'duplicate-id': f['elements'][1]['id'] = 'visitor'
    if mutation == 'dangling-role': f['elements'][-1]['roles'][0]['member'] = 'missing'
    if mutation == 'wrong-event': f['elements'][9]['trigger'] = 'visitor'
    if mutation == 'unpinned':
        e = copy.deepcopy(f['elements'][0]); e.update(id='sub', kind='subflow', flow_id='other', revision_digest='latest')
        del e['type']; del e['ref']; f['elements'].append(e)
    if mutation == 'nan': f['elements'][0]['props']['bad'] = float('nan')
    if mutation == 'code-constraint':
        e = copy.deepcopy(f['elements'][0]); e.update(id='c', kind='constraint', predicate='eval', members=['visitor'])
        del e['type']; del e['ref']; f['elements'].append(e)
    with pytest.raises(ValueError): validate(f)


@pytest.mark.parametrize('mutation', ['extra', 'missing', 'duplicate', 'mixed', 'role-tamper', 'source-tamper', 'code'])
def test_projection_tamper_refused(mutation):
    f = garden(); atoms = project(f); d = digest(f)
    if mutation == 'extra': atoms.append(atom('OFEvil', d, 'anything'))
    if mutation == 'missing': atoms = [a for a in atoms if not a.startswith('(OFRole ')]
    if mutation == 'duplicate': atoms.append(atoms[0])
    if mutation == 'mixed': atoms.append(atom('OFTransition', 'b'*64, 't0', 'visitor', 'signup'))
    if mutation == 'role-tamper':
        atoms = [a for a in atoms if not a.startswith('(OFRole ')] + [atom('OFRole', d, 'volunteers', 'wrong', 0, 'visitor')]
    if mutation == 'source-tamper':
        target = atom('OFField', d, 'visitor', 'props', {'control_step': True})
        atoms[atoms.index(target)] = atom('OFField', d, 'visitor', 'props', {'control_step': False})
    if mutation == 'code': atoms.append('!(evil &self)')
    with pytest.raises(ValueError): recover(atoms)


def test_checks_are_structural_and_never_authority():
    f = garden(); result = check_structure(f)
    assert result['findings'] == [] and result['execution_authorized'] is False
    f['elements'][11]['approver'] = None
    f['elements'][10]['from'] = 'welcome'
    codes = {x['code'] for x in check_structure(f)['findings']}
    assert {'missing-approver', 'unreachable-step'} <= codes


def test_independent_metadata():
    f = garden(); m = f['elements'][-1]['meta']
    m.update(origin='inferred', confidence=.6, evidence=['synthetic:evidence'], revision_state='adopted')
    assert recover(project(f)) == f


def test_revision_snapshot_does_not_alias_input():
    f = garden(); r = revision(f)
    f['elements'][0]['props']['new'] = True
    assert r['digest'] == digest(r['body']) and r['body'] != f


@pytest.mark.parametrize('field', ['kind', 'origin', 'revision_state', 'runtime_state'])
def test_malformed_enum_is_a_validation_error(field):
    f = garden()
    if field == 'kind': f['elements'][0][field] = []
    else: f['elements'][0]['meta'][field] = []
    with pytest.raises(ValueError): validate(f)


def test_dangling_layout_and_nonfinite_position_rejected():
    with pytest.raises(ValueError): revision(garden(), {'missing': {'x': 0, 'y': 0}})
    with pytest.raises(ValueError): revision(garden(), {'visitor': {'x': float('inf'), 'y': 0}})
