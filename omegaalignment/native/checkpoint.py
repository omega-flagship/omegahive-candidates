"""Opaque local checkpoint carrier. Reading never evaluates MeTTa or grants authority."""
import hashlib
import json
import os
from pathlib import Path
import tempfile

MAX_BYTES = 65536

def save(path: Path, payload: bytes, binding: dict[str, str]) -> str:
    if not isinstance(payload, bytes) or not payload or len(payload) > MAX_BYTES:
        raise ValueError('invalid payload size')
    if not binding or any(not isinstance(k, str) or not isinstance(v, str) for k, v in binding.items()):
        raise ValueError('invalid binding')
    digest = hashlib.sha256(payload).hexdigest()
    record = {'version': 1, 'binding': binding, 'digest': digest, 'payload': payload.decode('utf-8')}
    encoded = json.dumps(record, ensure_ascii=False, sort_keys=True).encode('utf-8')
    if len(encoded) > MAX_BYTES * 8:
        raise ValueError('oversized record')
    fd, temp = tempfile.mkstemp(prefix='.checkpoint-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return digest

def load(path: Path, *, expected_digest: str, expected_binding: dict[str, str]) -> bytes:
    # Expectations must come from a separately trusted receipt, not this file.
    with path.open('rb') as stream:
        raw = stream.read(MAX_BYTES * 8 + 1)
    if len(raw) > MAX_BYTES * 8:
        raise ValueError('oversized record')
    try:
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError('duplicate field')
                result[key] = value
            return result
        record = json.loads(raw, object_pairs_hook=unique)
        if not isinstance(record, dict) or set(record) != {'version', 'binding', 'digest', 'payload'}:
            raise ValueError('invalid record')
        if type(record['version']) is not int or record['version'] != 1 or record['binding'] != expected_binding:
            raise ValueError('wrong binding or version')
        if not isinstance(record['payload'], str):
            raise ValueError('invalid payload')
        payload = record['payload'].encode('utf-8')
        if not payload or len(payload) > MAX_BYTES:
            raise ValueError('invalid payload size')
        actual = hashlib.sha256(payload).hexdigest()
        if record['digest'] != expected_digest or actual != expected_digest:
            raise ValueError('digest mismatch')
        return payload
    except (UnicodeError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError('malformed checkpoint') from exc
