"""L1 real host scope transport observation, not recipient-skill acceptance."""
import hashlib,json
from omegalearn.tests.host_artifact_probes import client
from hive.tests.test_core_api import make_swarm_and_agents

def test_host_refuses_package_scope_and_binds_only_action_channels(client,tmp_path,monkeypatch):
    folder=tmp_path/'scope-probe';folder.mkdir()
    (folder/'plugin.json').write_text(json.dumps({'id':'learn-probe','name':'Learn scope probe','capabilities':[]}))
    (folder/'program.py').write_text('''
def describe():
 return {'contract':'0.2','kinds':[{'id':'status','role':'assessment'}],'relations':[],'actions':[{'id':'acknowledge-package','label':'Acknowledge','applies_to':['status'],'agents':True}]}
def view(ctx,focus,stage):
 return {'revision':'1','items':[{'id':'probe','kind':'status','label':'Synthetic scope transport'}]}
def act(ctx,action,items,params):
 return {'status':'refused'}
def offer(ctx,mind):
 return {'actor_preview':{'actor':'synthetic-recipient'},'actions_offered':['acknowledge-package'],'channels_offered':[]}
def bind(ctx,mind,scope,operation_key):
 global observed
 observed=scope
 return {'actor':'synthetic-recipient'}
def unbind(ctx,attachment,operation_key):
 return {}
''')
    monkeypatch.setenv('HIVE_PLUGIN_DIRS',str(folder));client.post('/api/programs/reload')
    swarm,(a,b)=make_swarm_and_agents(client)
    h=client.app.state.hive;h.db.insert('people',{'id':'u_learn','email':'learn@example.invalid','name':'Synthetic admin','role':'admin','created_at':'fixture'})
    token=client.headers['Authorization'].split()[1]
    h.db.execute("UPDATE sessions SET kind='sso',principal='user:u_learn' WHERE token_hash=?",(hashlib.sha256(token.encode()).hexdigest(),))
    assert client.post('/api/programs/learn-probe/activations',json={'swarm_id':swarm['id']}).status_code==200
    pin={'id':'repair','version':'1','artifact_id':'synthetic-artifact','revision':1,'digest':'sha256:'+'a'*64}
    r=client.post('/api/programs/learn-probe/attachments',json={'mind_id':a['id'],'actions':['acknowledge-package'],'channels':[],
        'policy':{'acknowledge-package':'allow'},'idempotency_key':'pin1','scope':{'package':pin}})
    assert r.status_code==400 and r.json()['error']['message']=='unknown attachment fields'
    r=client.post('/api/programs/learn-probe/attachments',json={'mind_id':a['id'],'actions':['acknowledge-package'],'channels':[],
        'policy':{'acknowledge-package':'allow'},'idempotency_key':'unpinned'})
    assert r.status_code==200,r.text
    module=h.programs._ready('learn-probe')['module']
    assert module.observed=={'actions':['acknowledge-package'],'channels':[]}
    assert 'package' not in r.json()

