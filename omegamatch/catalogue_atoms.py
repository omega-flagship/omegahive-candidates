"""Catalogue data codec; D2 output reuses OmegaAtom via catalogue_sidecars.

Legacy catalogue_atoms is an L0 literal sample serializer, not host publication.
"""


def symbol(value):
    if not isinstance(value, str) or not value or len(value.encode('utf-8')) > 8192:
        raise ValueError('invalid catalogue string')
    return 's' + value.encode('utf-8').hex()


def decode_symbol(value):
    if not isinstance(value, str) or not value.startswith('s'):
        raise ValueError('invalid encoded symbol')
    return bytes.fromhex(value[1:]).decode('utf-8')


def catalogue_atoms(catalogue):
    """Return literal facts only. Visibility remains the host's responsibility.

    Hex symbols preserve strings without allowing parentheses, grounded calls,
    comments or evaluation syntax to become program text. No capability fit,
    negative existence, performance, grant or execution fact is derived.
    """
    if not isinstance(catalogue, dict) or type(catalogue.get('truncated')) is not bool:
        raise ValueError('invalid catalogue coverage')
    digest = symbol(catalogue['catalogue_digest'])
    scope = symbol(catalogue['requester_swarm'])
    offers = catalogue['offers']
    if not isinstance(offers, list) or len(offers) > 10000:
        raise ValueError('invalid offer collection')
    facts = [f'(Catalogue {digest} {scope})',
             f'(Coverage {digest} {"incomplete" if catalogue["truncated"] else "projection-complete"})']
    for family, source_digest in catalogue.get('sources', {}).items():
        if source_digest is None:
            facts.append(f'(SourceUnavailable {digest} {symbol(family)})')
        else:
            facts.append(f'(SourceDigest {digest} {symbol(family)} {symbol(source_digest)})')
    for unknown in catalogue.get('unknowns', []):
        facts.append(f'(CatalogueUnknown {digest} {symbol(unknown)})')
    seen = set()
    for offer in offers:
        oid = symbol(offer['id'])
        if oid in seen:
            raise ValueError('duplicate offer')
        seen.add(oid)
        tier = offer['tier']
        if tier not in {'declared', 'advertised', 'demonstrated', 'reviewed'}:
            raise ValueError('invalid evidence tier')
        facts.append(f'(CatalogueOffer {digest} {oid} {symbol(offer["provider"]["kind"])} {symbol(offer["provider"]["id"])} {symbol(offer["capability"]["name"])} {symbol(offer["capability"]["source"])} {tier})')
        offer_scope = offer['scope']
        if type(offer_scope.get('connection_only')) is not bool:
            raise ValueError('invalid connection scope')
        connection = 'connection-only' if offer_scope['connection_only'] else 'ordinary'
        facts.append(f'(OfferScope {digest} {oid} {symbol(offer_scope["visibility"])} {connection})')
        if 'swarm_id' in offer_scope:
            facts.append(f'(OfferSwarm {digest} {oid} {symbol(offer_scope["swarm_id"])})')
        unknowns, evidence = offer['unknowns'], offer['evidence']
        if not isinstance(unknowns, list) or not isinstance(evidence, list) or len(unknowns) + len(evidence) > 1000:
            raise ValueError('invalid offer evidence')
        for unknown in unknowns:
            facts.append(f'(OfferUnknown {digest} {oid} {symbol(unknown)})')
        for item in evidence:
            facts.append(f'(OfferEvidence {digest} {oid} {symbol(item["kind"])} {symbol(item["ref"])} {symbol(item["digest"])})')
    return '\n'.join(sorted(set(facts))) + '\n'


def catalogue_statements(catalogue):
    """Inert trees from the bounded literal codec; no parsing of external MeTTa."""
    return [line[1:-1].split(' ') for line in catalogue_atoms(catalogue).splitlines()]


def catalogue_sidecars(catalogue, host_snapshot):
    """Project through OmegaAtom D2, using only supplied host-bound identities.

    Caller supplies the complete host-issued snapshot. This helper authenticates
    nothing, allocates no ids/stamps/truth and never publishes or integrates.
    Metadata truth remains unknown; runtime statuses stay catalogue assertions.
    """
    from omegaatom.envelope import validate, sidecars, canonical
    snapshot = validate(host_snapshot)
    expected = {canonical(atom) for atom in catalogue_statements(catalogue)}
    records = snapshot['records']
    if snapshot['scope'] != catalogue['requester_swarm']:
        raise ValueError('catalogue scope mismatch')
    source_digest = catalogue['catalogue_digest']
    if not isinstance(source_digest, str) or not source_digest.startswith('sha256:'):
        raise ValueError('catalogue source binding missing')
    if len(records) != len(expected) or {canonical(r['statement']) for r in records} != expected:
        raise ValueError('catalogue statement binding mismatch')
    for record in records:
        if record['source']['digest'] != source_digest[7:]:
            raise ValueError('catalogue source digest mismatch')
        if not record['unknown'] or 'truth' in record:
            raise ValueError('catalogue metadata truth must remain unknown')
        if record['status'] not in {'observed', 'borrowed-prior'} or record.get('premises'):
            raise ValueError('catalogue projection cannot invent inference')
    return sidecars(snapshot)
