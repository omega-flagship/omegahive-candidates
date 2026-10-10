import json
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import pytest
from omegaflow.editor.server import Handler
from omegaflow.examples.garden import garden
from omegaflow import digest


@pytest.fixture
def local_server():
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    yield server.server_port
    server.shutdown();server.server_close();thread.join()


def request(port, method, path, value=None, **headers):
    connection = HTTPConnection('127.0.0.1', port, timeout=3)
    payload = json.dumps(value) if value is not None else None
    connection.request(method,path,payload,headers={'Content-Type':'application/json',**headers})
    response=connection.getresponse(); body=response.read(); status=response.status; connection.close()
    return status,body


def test_server_uses_shared_revision_and_has_no_run_endpoint(local_server):
    f=garden();status,raw=request(local_server,'POST','/api/validate',{'body':f,'layout':{}})
    data=json.loads(raw)
    assert status == 200 and data['revision']['digest']==digest(f)
    assert data['check']['execution_authorized'] is False
    assert data['preflight']['execution_authorized'] is False and not data['preflight']['structurally_eligible']
    assert request(local_server,'POST','/api/run',{})[0]==404


@pytest.mark.parametrize('headers',[{'Origin':'https://untrusted.example'},{'Host':'untrusted.example'}])
def test_cross_origin_and_rebinding_refused(local_server,headers):
    assert request(local_server,'POST','/api/validate',{'body':garden(),'layout':{}},**headers)[0]==403


def test_invalid_and_oversized_requests_refused(local_server):
    assert request(local_server,'POST','/api/validate',{'body':{},'layout':{}})[0]==400
    # The server refuses an oversized declaration before consuming its body.
    connection=HTTPConnection('127.0.0.1',local_server,timeout=3)
    connection.putrequest('POST','/api/validate')
    connection.putheader('Content-Type','application/json');connection.putheader('Content-Length','300001');connection.endheaders()
    response=connection.getresponse();assert response.status==413;response.read();connection.close()
    assert request(local_server,'POST','/api/validate',{'body':garden(),'layout':{}},**{'Content-Type':'text/plain'})[0]==415
    assert request(local_server,'GET','/../../CLAUDE.md')[0]==404


def test_templates_are_read_only_drafts(local_server):
    status, raw = request(local_server, 'GET', '/api/templates')
    assert status == 200
    assert len(json.loads(raw)['templates']) == 5
    assert request(local_server, 'GET', '/api/templates', Origin='https://untrusted.example')[0] == 403
