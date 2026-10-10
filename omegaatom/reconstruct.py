"""Bounded data-only reconstruction in a fresh process; no host/interpreter."""
import json
import sys
from .envelope import loads, digest, lineage_state, Refused


def main():
    try:
        raw = sys.stdin.buffer.read(2_000_001)
        snapshot = loads(raw.decode("utf-8"))
        print(json.dumps({"snapshot_digest": digest(snapshot), "states": lineage_state(snapshot)}, separators=(",", ":")))
    except (Refused, UnicodeError) as error:
        print(f"schema_invalid: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
