"""Self-contained read-only presentation; no imported candidate code execution."""
import json
import hashlib
from pathlib import Path

def describe():
    return {'contract':'0.1','kinds':[{'id':'component','label':'Component','role':'other'},
        {'id':'experiment','label':'Experiment','role':'assessment'},{'id':'gap','label':'Gap','role':'gap'}],
        'relations':[], 'actions':[]}

def view(ctx, focus=None, stage=None):
    path=Path(__file__).with_name('catalogue.json'); data=path.read_bytes()
    catalogue=json.loads(data)
    return {'revision':hashlib.sha256(data).hexdigest(),'title':'OmegaLearn: learning workshop',
            'focus':focus or 'symbolic-repair','items':catalogue['items'],'links':[]}

def act(ctx, action, items, params=None, base_revision=None):
    return {'status':'refused','message':'Read-only L0 catalogue. Build, evidence intake and recipient attachment require the separately scoped host route.'}
