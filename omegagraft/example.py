"""Read only the packaged synthetic fixture and print L0 advice."""
import json
from pathlib import Path
from . import validate_manifest, blast_radius, propose_swap


def main():
    data = json.loads(Path(__file__).with_suffix('.json').read_text())
    for manifest in data['manifests']:
        validate_manifest(manifest, data['slots'])
    print(json.dumps({
        'unplug': blast_radius(data['snapshot'], data['slots'], 'old'),
        'swap': propose_swap(data['snapshot'], data['slots'], 'required', 'lookup', 'new'),
    }, indent=2))


if __name__ == '__main__':
    main()
