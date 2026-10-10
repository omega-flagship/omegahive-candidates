"""Explicit bridges to owner validators and existing host artifact APIs."""
from .core import Refused, copy, canonical, digest

def evidence_ref(eid):
    from omegaatom.envelope import format_evidence_ref
    return format_evidence_ref(eid)

def atom_resolver(event, snapshot, trusted):
    """trusted is a host-derived grant/current-source record, never model output.

    Atom validates representation/lineage; the host still establishes custody.
    Integer Atom source revisions map to Learn's opaque decimal string revisions.
    """
    from omegaatom.envelope import validate, lineage_state
    checked = validate(snapshot)
    index={evidence_ref(r['id']):r for r in checked['records']}
    states={evidence_ref(r['id']):r for r in lineage_state(checked)}
    for ref in event['evidence_refs']:
        r=index.get(ref)
        if r is None or states[ref]['retracted'] or states[ref]['stale']:
            raise Refused('Atom evidence absent/retracted/stale')
        expected={'id':r['source']['subject'],'revision':str(r['source']['revision']),'digest':r['source']['digest']}
        if expected!=event['subject'] or r['source']['owner']!=event['owner'] or r['scope']!=event['scope']:
            raise Refused('Atom source binding mismatch')
    result=copy(trusted)
    # Caller cannot declare non-Atom evidence visible through this adapter.
    result['visible_refs']=[r for r in result.get('visible_refs',[]) if r not in event['evidence_refs'] or r in index]
    return result

def publish_candidate(ctx, ledger, key):
    """Publication of a proposal only. No recipient attachment, adoption or writes."""
    p=ledger.package(key)
    if p.pop('local_status')=='stale': raise Refused('stale candidate')
    out=ctx.publish('improvement-package',f"{p['id']} version {p['version']}",canonical(p))
    observed=ctx.read_revision(out['artifact_id'],out['revision'])
    if observed['digest']!=out['digest'] or observed['body']!=canonical(p):
        raise Refused('published artifact readback mismatch')
    return {'package':key,'package_digest':p['digest'],'artifact':copy(out),'stage':'published-proposal',
            'delivered':False,'acknowledged':False,'attached':False,'callable':False,'measured-useful':False}


def resolve_artifact_export(ctx, event, trusted):
    """Read the exact owner-export under actor-scoped artifacts:read.

    trusted current_subject/grants/ref eligibility must come from the host.
    Reading an older revision is allowed by the host but not proof of freshness.
    """
    binding = event['subject']
    if trusted.get('current_subject') != binding:
        raise Refused('stale source export')
    try:
        number = int(binding['revision'])
    except (ValueError, TypeError):
        raise Refused('artifact revision must be decimal integer')
    if str(number) != binding['revision'] or number < 1:
        raise Refused('artifact revision must be canonical positive integer')
    row = ctx.read_revision(binding['id'], number)
    if row['digest'] != 'sha256:'+binding['digest'] or row['author'] != event['owner']:
        raise Refused('source export binding mismatch')
    return copy(trusted)


def atom_query_resolver(event, snapshot, trusted, *, closure_complete):
    """Resolve one normalized S3 scope page, after host actor/grant checks.

    Transport callers extract the scope snapshot and explicit closure flag.
    result_complete may be false: a page is usable only if its own lineage is
    complete. This function neither merges pages nor retains grant authority.
    """
    if closure_complete is not True:
        raise Refused('query page has incomplete or unspecified lineage')
    return atom_resolver(event, snapshot, trusted)
