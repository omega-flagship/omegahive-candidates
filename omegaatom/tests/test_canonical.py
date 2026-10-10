"""Byte-compatibility guard for the accepted snapshot hash contract."""
import hashlib
import pytest
from omegaatom.envelope import canonical, digest


@pytest.mark.parametrize("value, expected", [
    ({"z": 1, "a": "é"}, '{"a":"\\u00e9","z":1}'),
    (["😀", "\n", 1, 1.0, -0.0], '["\\ud83d\\ude00","\\n",1,1.0,-0.0]'),
    ({"b": [2, 1], "a": {}}, '{"a":{},"b":[2,1]}'),
])
def test_exact_canonical_bytes(value, expected):
    assert canonical(value) == expected
    assert digest(value) == hashlib.sha256(expected.encode('utf-8')).hexdigest()


def test_order_and_number_representation_are_preserved():
    assert digest({"b": 2, "a": 1}) == digest({"a": 1, "b": 2})
    assert digest([1, 2]) != digest([2, 1])
    assert digest(1) != digest(1.0)


@pytest.mark.parametrize("number", [float('nan'), float('inf'), -float('inf')])
def test_nonfinite_json_never_hashed(number):
    with pytest.raises(ValueError):
        digest(number)
