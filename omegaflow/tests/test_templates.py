import pytest
from omegaflow import digest, project, recover, revision
from omegaflow.admission import prepare
from omegaflow.examples.templates import catalogue


@pytest.mark.parametrize('template', catalogue(), ids=lambda t: t['key'])
def test_starter_is_portable_and_has_no_authority(template):
    value = template['revision']; body = value['body']
    assert value['digest'] == digest(body)
    assert recover(project(body)) == body
    assert revision(body, {})['digest'] == value['digest']
    assert value['execution_authority'] == 'none'
    assert prepare(body)['execution_authorized'] is False
    assert all(e['meta']['revision_state'] == 'draft' for e in body['elements'])
    assert all(not e['meta']['evidence'] for e in body['elements'])


def test_catalogue_is_detached_and_preserves_ordered_relation_members():
    first = catalogue(); first[0]['revision']['body']['elements'][0]['props']['label'] = 'Changed'
    assert catalogue()[0]['revision']['body']['elements'][0]['props']['label'] == 'Intake'
    connections = next(t for t in catalogue() if t['key'] == 'connection-map')['revision']['body']
    members = {e['id']:e for e in connections['elements']}
    assert [r['name'] for r in members['connection']['roles']] == ['requester','provider','service','scope']
    assert members['connection-ownership']['roles'][0]['member'] == 'connection'
    assert not any(e['kind'] == 'transition' for e in connections['elements'])
