from copy import deepcopy
import pytest
from omegamatch.catalogue_atoms import catalogue_atoms, symbol, decode_symbol


def catalogue():
    return {'catalogue_digest': 'sha256:synthetic', 'requester_swarm': 'swarm:synthetic', 'truncated': True,
            'sources': {'skills': None, 'services': 'sha256:service'}, 'unknowns': ['skills-not-projected'],
            'offers': [{'id': 'offer:synthetic', 'provider': {'kind': 'swarm', 'id': 'swarm:provider'},
                        'capability': {'name': 'planning', 'source': 'service'}, 'tier': 'advertised',
                        'scope': {'visibility': 'private', 'connection_only': True}, 'unknowns': ['performance'], 'evidence': [{'kind': 'config', 'ref': 'synthetic-ref', 'digest': 'sha256:config'}]}]}


def test_projection_preserves_metadata_unknowns_and_incomplete_scope():
    data = catalogue(); text = catalogue_atoms(data)
    assert f'(Catalogue {symbol(data["catalogue_digest"])} {symbol(data["requester_swarm"])})' in text
    assert ' incomplete)' in text and ' advertised)' in text
    assert '(OfferUnknown ' in text and '(OfferEvidence ' in text
    assert '(SourceUnavailable ' in text and ' connection-only)' in text
    assert not any(word in text for word in ['Grant', 'Fit', 'Accepted', 'Execute', 'NoCandidate'])


def test_strings_cannot_inject_rules_or_effects():
    malicious = ')\n!(shell "synthetic")\n(= (x) grounded-call) ; Ω'
    data = catalogue(); data['offers'][0]['capability']['name'] = malicious
    text = catalogue_atoms(data)
    assert malicious not in text and '!' not in text and ';' not in text and 'shell' not in text
    assert decode_symbol(symbol(malicious)) == malicious
    assert all(line.startswith('(') and line.endswith(')') for line in text.splitlines())


def test_projection_is_deterministic_and_does_not_mutate_input():
    data = catalogue(); original = deepcopy(data)
    assert catalogue_atoms(data) == catalogue_atoms(data)
    assert data == original


@pytest.mark.parametrize('mutation', ['duplicate', 'tier', 'coverage'])
def test_bad_projection_refused(mutation):
    data = catalogue()
    if mutation == 'duplicate': data['offers'] *= 2
    if mutation == 'tier': data['offers'][0]['tier'] = 'accepted-performance'
    if mutation == 'coverage': data['truncated'] = 'false'
    with pytest.raises(ValueError): catalogue_atoms(data)


def host_bound():
    from omegamatch.catalogue_atoms import catalogue_statements
    data = catalogue(); data['catalogue_digest'] = 'sha256:' + 'a' * 64
    rows = []
    for n, atom in enumerate(catalogue_statements(data), 1):
        eid = ['ev', 'synthetic-host', n]
        rows.append({'id': eid, 'statement': atom,
                     'source': {'owner': 'synthetic-host', 'subject': 'catalogue', 'revision': 1, 'digest': 'a' * 64},
                     'status': 'observed', 'scope': data['requester_swarm'], 'stamp': [eid], 'unknown': True})
    return data, {'version': '0.1', 'owner': 'synthetic-host', 'scope': data['requester_swarm'], 'revision': 1, 'records': rows}


def test_atom_envelope_adapter_reuses_authoritative_sidecars_and_retains_unknown():
    from omegamatch.catalogue_atoms import catalogue_sidecars
    from omegaatom.envelope import sidecars
    data, snapshot = host_bound(); original = deepcopy(snapshot)
    assert catalogue_sidecars(data, snapshot) == sidecars(snapshot)
    assert not any(atom[0] in {'Asserted', 'Current'} for atom in catalogue_sidecars(data, snapshot))
    assert snapshot == original


@pytest.mark.parametrize('change', ['scope', 'digest', 'statement', 'truth', 'identity'])
def test_envelope_adapter_refuses_binding_and_identity_drift(change):
    from omegamatch.catalogue_atoms import catalogue_sidecars
    data, snapshot = host_bound()
    if change == 'scope': data['requester_swarm'] = 'other'
    if change == 'digest': data['catalogue_digest'] = 'sha256:' + 'b' * 64
    if change == 'statement': snapshot['records'][0]['statement'] = ['Invented', 'fact']
    if change == 'truth':
        snapshot['records'][0]['unknown'] = False
        snapshot['records'][0]['truth'] = ['stv', 1, 0.5]
    if change == 'identity': snapshot['records'][0]['id'] = ['ev', 'synthetic-host', 0]
    with pytest.raises(ValueError): catalogue_sidecars(data, snapshot)
