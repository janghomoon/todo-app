"""표준 라이브러리로 실행하는 로컬 할 일 앱."""
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT.parent / 'frontend'
DATA = Path(os.environ.get('TODO_DATA_FILE', str(ROOT / 'data' / 'todos.json')))


def read_todos():
    if not DATA.exists():
        return []
    return json.loads(DATA.read_text(encoding='utf-8'))


def save_todos(todos):
    DATA.parent.mkdir(parents=True, exist_ok=True)
    temporary = DATA.with_suffix('.tmp')
    temporary.write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(DATA)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND), **kwargs)

    def json_response(self, status, value):
        body = json.dumps(value, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if urlsplit(self.path).path.startswith('/api/'):
            self.handle_api('GET')
        else:
            # 문서·지침 파일과 디렉터리 목록은 정적 경로에 노출하지 않는다.
            if urlsplit(self.path).path not in ('/', '/index.html', '/css/style.css', '/js/app.js'):
                self.send_error(404)
                return
            super().do_GET()

    def do_HEAD(self):
        self.send_error(405)

    def do_POST(self):
        self.handle_api('POST')

    def do_PATCH(self):
        self.handle_api('PATCH')

    def do_DELETE(self):
        self.handle_api('DELETE')

    def handle_api(self, method):
        try:
            self.route_api(method)
        except (ValueError, UnicodeDecodeError):
            self.json_response(400, {'error': '올바른 JSON 입력을 보내 주세요.'})
        except OSError:
            self.json_response(500, {'error': '할 일을 읽거나 저장하지 못했습니다.'})

    def route_api(self, method):
        path = urlsplit(self.path).path
        parts = path.strip('/').split('/')
        if parts[:2] != ['api', 'todos'] or len(parts) not in (2, 3):
            self.json_response(404, {'error': '존재하지 않는 경로입니다.'})
            return
        if (len(parts) == 2 and method not in ('GET', 'POST')) or (len(parts) == 3 and method not in ('PATCH', 'DELETE')):
            self.json_response(405, {'error': '지원하지 않는 요청입니다.'})
            return
        todos = read_todos()
        if method == 'GET':
            self.json_response(200, todos)
            return
        body = {}
        if method in ('POST', 'PATCH'):
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 4096:
                self.json_response(400, {'error': '입력 크기가 올바르지 않습니다.'})
                return
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError('Expected object')
        if method == 'POST':
            title = body.get('title')
            if not isinstance(title, str) or not 1 <= len(title.strip()) <= 200:
                self.json_response(400, {'error': '할 일은 1~200자로 입력해 주세요.'})
                return
            todo = {'id': str(uuid4()), 'title': title.strip(), 'completed': False}
            todos.append(todo)
            save_todos(todos)
            self.json_response(201, todo)
            return
        todo = next((item for item in todos if item['id'] == parts[2]), None)
        if todo is None:
            self.json_response(404, {'error': '할 일을 찾을 수 없습니다.'})
            return
        if method == 'PATCH':
            if type(body.get('completed')) is not bool:
                self.json_response(400, {'error': '완료 상태는 true 또는 false여야 합니다.'})
                return
            todo['completed'] = body['completed']
            save_todos(todos)
            self.json_response(200, todo)
        else:
            save_todos([item for item in todos if item['id'] != todo['id']])
            self.json_response(200, {'ok': True})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f'할 일 앱: http://127.0.0.1:{port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
