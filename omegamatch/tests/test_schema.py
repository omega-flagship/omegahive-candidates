import importlib.util
import json
from pathlib import Path
import pytest
from omegamatch.schema import reuse_alert_schema
from omegamatch.tests.test_protocol import fixture

# Read/load the host's pure validator only; no app, store, routes or worker.
# The host is the omegahive repository's `hive` package, found on PYTHONPATH.
path=Path(importlib.util.find_spec('hive').origin).parent/'core/result_schema.py'
spec=importlib.util.spec_from_file_location('omegamatch_host_result_schema',path)
host=importlib.util.module_from_spec(spec)
spec.loader.exec_module(host)


def test_schema_uses_host_subset_and_valid_example():
    inputs,output=fixture()
    schema=reuse_alert_schema(inputs['binding'],inputs['need_id'])
    assert host.check_schema(schema)==schema
    assert host.validate(output,schema)==[]


@pytest.mark.parametrize('change',[
    {'authority':'execute'}, {'execution_authorized':True},
    {'evidence_refs':[]}, {'target_kind':'agent'},
    {'rationale':'   '}, {'need_id':'other'},
])
def test_host_shape_validator_refuses_forbidden_results(change):
    inputs,output=fixture()
    output.update(change)
    assert host.validate(output,reuse_alert_schema(inputs['binding'],inputs['need_id']))


def test_host_rejects_changed_binding():
    inputs,output=fixture()
    output['binding']['catalogue_digest']='changed'
    assert host.validate(output,reuse_alert_schema(inputs['binding'],inputs['need_id']))


def test_schema_is_not_content_acceptance():
    inputs,output=fixture()
    output['evidence_refs'][0]['basis']='accepted-performance'
    assert host.validate(output,reuse_alert_schema(inputs['binding'],inputs['need_id']))==[]
    # Evidence admission is separately tested to reject this promotion.


def test_checked_in_schema_matches_generator():
    path=Path(__file__).resolve().parents[1]/'reuse-alert.schema.json'
    assert json.loads(path.read_text())==reuse_alert_schema()
