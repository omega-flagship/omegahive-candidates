"""Prepared S6 hook helpers. Frozen r2.6 binding; host transport remains pending."""
import json
import re

BIND_ACCEPTS_BINDING = True
from .core import Refused, copy, canonical


def bind_package(ctx, mind, scope, attachment_id, binding, inspect_package):
    """Exact read + fresh eligibility inspection; no adoption or rule execution.

    inspect_package is a trusted current-source validator supplied by the host
    integration. It returns the validated package plus local_status. Artifact
    digest and package content digest remain separate bindings.
    """
    if type(scope) is not dict or set(scope) != {'actions','channels'}:
        raise Refused('exact package attachment scope required')
    pin=binding
    if type(pin) is not dict or set(pin) != {'kind','id','version','artifact_id','revision','digest'}:
        raise Refused('exact artifact package pin required')
    if pin['kind'] != 'improvement-package' or type(pin['digest']) is not str or not re.fullmatch(r'sha256:[a-f0-9]{64}', pin['digest']):
        raise Refused('invalid binding kind or wire digest')
    if any(type(pin[k]) is not str or not pin[k] for k in ('id','version','artifact_id','digest')) or type(pin['revision']) is not int or pin['revision'] < 1:
        raise Refused('invalid artifact package pin')
    if not attachment_id or type(mind) is not dict or not mind.get('id'):
        raise Refused('recipient attachment identity required')
    row=ctx.read_revision(pin['artifact_id'],pin['revision'])
    if row['digest'] != pin['digest']:
        raise Refused('attachment artifact digest mismatch')
    try: package=json.loads(row['body'])
    except (ValueError,TypeError): raise Refused('invalid package artifact')
    if type(package) is not dict or package.get('id') != pin['id'] or package.get('version') != pin['version'] or row['body'] != canonical(package):
        raise Refused('attachment package identity mismatch')
    checked=inspect_package(copy(package))
    if type(checked) is not dict or checked.pop('local_status',None) != 'proposed' or checked != package:
        raise Refused('attachment package stale or invalid')
    # Preserve binding separately until host persists/forwards it at dispatch.
    return {'actor':'learn-recipient:'+mind['id'], 'binding':{
        'attachment_id':attachment_id,'mind_id':mind['id'],'artifact_binding':copy(pin),
        'package_digest':package['digest']}}


def acknowledge_package(actor, bound):
    """Recipient action requires the host's exact attachment context each time."""
    if type(actor) is not dict or actor.get('kind') != 'mind' or actor.get('id') != bound['mind_id']:
        raise Refused('recipient agent required')
    attachment=actor.get('attachment')
    if type(attachment) is not dict or attachment.get('id') != bound['attachment_id'] or attachment.get('binding') != bound['artifact_binding']:
        raise Refused('recipient attachment binding missing or changed')
    return {'attachment_id':bound['attachment_id'],'package_digest':bound['package_digest'],
            'acknowledged':True,'callable':False,'measured-useful':False}
