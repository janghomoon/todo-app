# 오늘의 할 일

순수 HTML/CSS/JavaScript와 Python 표준 HTTP 서버로 만든 개인용 로컬 앱입니다.

## 실행

Python 3.9 이상에서 프로젝트 폴더를 열고 실행합니다. 추가 패키지는 필요하지 않습니다.

```sh
python3 backend/server.py
```

브라우저에서 http://127.0.0.1:8000 을 엽니다. 종료는 `Ctrl+C`입니다.
다른 포트가 필요하면 `PORT=8001 python3 backend/server.py`로 실행합니다.

## 기능과 구성

- 할 일 추가, 완료 표시·해제, 삭제 및 완료 개수 표시
- `backend/data/todos.json`에 자동 저장하여 서버 재시작 후에도 유지
- `frontend/index.html`: 화면 구조
- `frontend/css/style.css`: 반응형 스타일
- `frontend/js/app.js`: 화면 동작과 API 요청
- `backend/server.py`: API와 정적 파일 서버
- 각 폴더의 `AGENTS.md`: 해당 영역의 작업 지침

API는 `GET/POST /api/todos`, `PATCH/DELETE /api/todos/{id}`를 제공합니다.
개인용이며 사용자 계정이나 다중 사용자별 데이터 분리는 없습니다.
