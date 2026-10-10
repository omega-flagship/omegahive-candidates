import json
from unittest.mock import patch
import pytest
from omegaalignment.native.checkpoint import save, load, MAX_BYTES

BINDING = {'subject': 'synthetic', 'source': 'pinned-law', 'interpretation': 'v1'}

def test_roundtrip_and_inert_payload(tmp_path):
    path = tmp_path / 'checkpoint'
    payload = b'!(untrusted-executable-looking-term)'
    digest = save(path, payload, BINDING)
    assert load(path, expected_digest=digest, expected_binding=BINDING) == payload

@pytest.mark.parametrize('mutation', ['payload', 'digest', 'binding', 'version', 'extra', 'truncate'])
def test_corruption_refused(tmp_path, mutation):
    path = tmp_path / 'checkpoint'
    digest = save(path, b'(synthetic-state)', BINDING)
    data = json.loads(path.read_text())
    if mutation == 'payload': data['payload'] += 'tampered'
    elif mutation == 'digest': data['digest'] = '0' * 64
    elif mutation == 'binding': data['binding']['subject'] = 'other'
    elif mutation == 'version': data['version'] = True
    elif mutation == 'extra': data['authority'] = 'granted'
    if mutation == 'truncate': path.write_text('{')
    else: path.write_text(json.dumps(data))
    with pytest.raises(ValueError): load(path, expected_digest=digest, expected_binding=BINDING)

def test_failed_replace_preserves_old_checkpoint(tmp_path):
    path = tmp_path / 'checkpoint'
    digest = save(path, b'old', BINDING)
    with patch('omegaalignment.native.checkpoint.os.replace', side_effect=OSError('injected write failure')):
        with pytest.raises(OSError): save(path, b'new', BINDING)
    assert load(path, expected_digest=digest, expected_binding=BINDING) == b'old'
    assert list(tmp_path.iterdir()) == [path]

def test_oversized_payload_refused(tmp_path):
    with pytest.raises(ValueError): save(tmp_path / 'checkpoint', b'x' * (MAX_BYTES + 1), BINDING)

def test_duplicate_fields_refused(tmp_path):
    path = tmp_path / 'checkpoint'
    path.write_text('{"version":1,"version":1}')
    with pytest.raises(ValueError): load(path, expected_digest='none', expected_binding=BINDING)
