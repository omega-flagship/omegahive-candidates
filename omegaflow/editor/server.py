"""Stateless loopback authoring preview, with the authoritative Python model.
No storage, Hive access, provider calls, or execution endpoint.
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from omegaflow import revision, check_structure, project
from omegaflow.examples.garden import garden
from omegaflow.examples.templates import catalogue
from omegaflow.admission import prepare

ROOT = Path(__file__).parent
LIMIT = 300000


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args): pass

    def reply(self, status, value, content_type='application/json'):
        data = json.dumps(value, allow_nan=False).encode() if content_type == 'application/json' else value
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers(); self.wfile.write(data)

    def admitted(self):
        host = self.headers.get('Host', '')
        expected = f'127.0.0.1:{self.server.server_port}'
        origin = self.headers.get('Origin')
        return host == expected and (origin is None or origin == 'http://' + expected)

    def do_GET(self):
        if not self.admitted(): return self.reply(403, {'error': 'loopback origin required'})
        path = urlparse(self.path).path
        if path == '/api/templates': return self.reply(200, {'templates': catalogue()})
        if path == '/api/example': return self.reply(200, {'body': garden(), 'layout': {}})
        files = {'/': ('index.html', 'text/html; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8'), '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if path not in files: return self.reply(404, {'error': 'not found'})
        name, mime = files[path]
        self.reply(200, (ROOT / name).read_bytes(), mime)

    def do_POST(self):
        if not self.admitted(): return self.reply(403, {'error': 'loopback origin required'})
        if self.path != '/api/validate': return self.reply(404, {'error': 'not found'})
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.reply(415, {'error': 'JSON required'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= LIMIT: return self.reply(413, {'error': 'request size limit'})
            value = json.loads(self.rfile.read(length))
            if not isinstance(value, dict) or set(value) != {'body', 'layout'}: raise ValueError('body and layout required')
            r = revision(value['body'], value['layout'])
            self.reply(200, {'revision': r, 'check': check_structure(r['body']), 'atoms': project(r['body']), 'preflight': prepare(r['body'])})
        except (ValueError, TypeError, RecursionError, KeyError) as e:
            self.reply(400, {'error': str(e) or 'invalid flow'})


def serve(port=8766):
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    print(f'http://127.0.0.1:{server.server_port}/', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--port', type=int, default=8766)
    serve(parser.parse_args().port)
