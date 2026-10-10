import copy
from types import SimpleNamespace
import pytest
from omegalearn.core import canonical,Refused
from omegalearn.attachment import bind_package,acknowledge_package
from omegalearn.tests.test_foundation import setup


def prepared():
    ledger,e,key=setup();p=ledger.package(key);p.pop('local_status')
    row={'digest':'sha256:'+'a'*64,'body':canonical(p)}
    ctx=SimpleNamespace(read_revision=lambda *_:copy.deepcopy(row))
    pin={'kind':'improvement-package','id':p['id'],'version':p['version'],'artifact_id':'ar1','revision':1,'digest':row['digest']}
    scope={'actions':['acknowledge-package'],'channels':[]}
    scope_pin=(scope,pin)
    def inspect(value):
        assert value==p
        return ledger.package(key)
    return ledger,e,ctx,row,scope_pin,inspect


def test_exact_binding_and_agent_ack_keep_success_states_separate():
    l,e,ctx,row,scope_pin,inspect=prepared();scope,pin=scope_pin
    bound=bind_package(ctx,{'id':'mind'},scope,'at1',pin,inspect)['binding']
    receipt=acknowledge_package({'kind':'mind','id':'mind','attachment':{'id':'at1','binding':pin}},bound)
    assert receipt['acknowledged'] and not receipt['callable'] and not receipt['measured-useful']
    assert bound['package_digest'] != pin['digest']


@pytest.mark.parametrize('change',['digest','version','stale','unpinned'])
def test_bind_refuses_mismatch_and_withdrawal(change):
    l,e,ctx,row,scope_pin,inspect=prepared();scope,pin=scope_pin
    if change=='digest':pin['digest']='sha256:'+'b'*64
    if change=='version':pin['version']='2'
    if change=='stale':l.invalidate(e['id'],lambda _:True)
    if change=='unpinned':pin=None
    with pytest.raises(Refused):bind_package(ctx,{'id':'mind'},scope,'at1',pin,inspect)


def test_old_attachment_or_person_cannot_acknowledge():
    l,e,ctx,row,scope_pin,inspect=prepared();scope,pin=scope_pin;bound=bind_package(ctx,{'id':'mind'},scope,'at2',pin,inspect)['binding']
    for actor in ({'kind':'person','id':'mind'}, {'kind':'mind','id':'mind','attachment':{'id':'at1','binding':pin}}, {'kind':'mind','id':'other'}):
        with pytest.raises(Refused):acknowledge_package(actor,bound)
