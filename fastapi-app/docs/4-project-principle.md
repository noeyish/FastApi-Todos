# 프로젝트 구조 설계 원칙
## My TodoList 앱 — v5.0.0

---

## 1. 최상위 원칙 (공통)

| 원칙 | 내용 |
|------|------|
| **단일 책임** | 하나의 모듈/함수는 하나의 역할만 담당한다 |
| **명시적 의존성** | 암묵적 전역 상태보다 명시적 인자/주입을 우선한다 |
| **작은 커밋** | 기능 단위로 커밋하고, 커밋 메시지는 변경 의도를 기술한다 |
| **문서화는 코드와 동기화** | docs/ 파일은 구현 변경 시 함께 업데이트한다 |
| **보안 우선** | 인증/인가 로직은 비즈니스 로직보다 먼저 검증한다 |

---

## 2. 의존성 / 레이어 원칙

### 백엔드 레이어 구조
```
[Router Layer]     ← HTTP 요청/응답, JWT 인증 검증
      ↓
[Service Layer]    ← 비즈니스 로직, 유효성 검사
      ↓
[Repository/ORM]  ← SQLAlchemy DB 접근
      ↓
[Model Layer]      ← Pydantic 스키마, ORM 모델
```

### 의존성 규칙
- 상위 레이어는 하위 레이어에만 의존한다 (역방향 금지)
- Router는 Service를 직접 호출하고, DB에 직접 접근하지 않는다
- 외부 라이브러리 의존은 Service/Core 레이어에서만 사용한다

### 프론트엔드 레이어 구조
```
[Page/View]   ← 화면 렌더링, 이벤트 바인딩
      ↓
[API Client]  ← fetch 호출, Bearer 토큰 헤더 주입
      ↓
[State]       ← 로컬 상태 관리 (todos 배열, 로그인 상태)
```

---

## 3. 코드 / 네이밍 원칙

### 공통
- 함수/변수명은 동사+명사 조합으로 의도를 표현한다 (예: `get_todos`, `create_user`)
- 약어 사용을 지양하고 풀네임을 사용한다 (예: `usr` → `user`)
- 매직 넘버/문자열은 상수로 정의한다

### 백엔드 (Python / FastAPI)
| 구분 | 규칙 | 예시 |
|------|------|------|
| 파일명 | snake_case | `todo_service.py`, `auth.py` |
| 클래스명 | PascalCase | `TodoCreate`, `UserResponse` |
| 함수명 | snake_case | `get_todos()`, `toggle_todo()` |
| 상수 | UPPER_SNAKE_CASE | `SECRET_KEY`, `ALGORITHM` |
| Pydantic 모델 | 용도 suffix | `TodoCreate`, `TodoResponse`, `UserLogin` |

### 프론트엔드 (HTML/JS)
| 구분 | 규칙 | 예시 |
|------|------|------|
| 함수명 | camelCase | `fetchTodos()`, `toggleComplete()` |
| CSS 클래스 | kebab-case | `todo-card`, `badge-high` |
| HTML id | kebab-case | `todo-list`, `add-form` |
| 상수 | UPPER_SNAKE_CASE | `BASE_URL` |

---

## 4. 테스트 / 품질 원칙

| 원칙 | 세부 내용 |
|------|-----------|
| **테스트 가능 단위** | 함수는 side-effect를 최소화하여 단위 테스트가 가능하도록 작성 |
| **인수 기준 기반 테스트** | PRD의 AC(인수 기준)별로 최소 1개 테스트 케이스 작성 |
| **엣지 케이스 명시** | 빈 제목, 중복 이메일, 만료 토큰 등 경계 조건 테스트 포함 |
| **테스트 격리** | 테스트 간 DB/상태 공유 금지 — 각 테스트는 독립 실행 가능 |
| **정적 분석** | SonarQube Quality Gate 통과 필수 |

### 테스트 구조
```
tests/
├── test_api.py              # API 통합 테스트 (pytest + httpx)
├── test_ui_playwright.py    # UI 테스트 — Playwright (MCP 연동)
├── test_ui_selenium.py      # UI 테스트 — Selenium (WebDriver)
└── conftest.py              # 공통 fixtures
```

---

## 5. 설정 / 보안 / 운영 원칙

### 설정
- 환경변수는 `.env` 파일로 관리하고, `.env.example`을 함께 커밋한다
- `.env`는 `.gitignore`에 포함한다
- 필수 환경변수: `SECRET_KEY`, `DATABASE_URL`, `ACCESS_TOKEN_EXPIRE_MINUTES`

### 보안
| 항목 | 원칙 |
|------|------|
| 비밀번호 | bcrypt로 해시 저장, 평문 저장 금지 |
| JWT | HS256 알고리즘, 만료 시간 설정 (기본 30분) |
| 인가 | 모든 Todo API에 `Depends(get_current_user)` 적용 |
| 데이터 격리 | Todo 조회/수정/삭제 시 `user_id` 일치 여부 검증 |

### 운영
- Docker Compose로 app + db + sonarqube 단일 명령 실행
- Jenkins 파이프라인: 테스트 → SonarQube 분석 → Docker 빌드/푸시 → 배포
- API 오류 응답은 `{"detail": "메시지"}` 형식으로 통일

---

## 6. 디렉토리 구조

```
fastapi-app/
├── main.py                    # FastAPI 앱 초기화, 라우터 등록
├── .env                       # 환경변수 (gitignore)
├── requirements.txt           # 의존성 목록
├── Dockerfile                 # Docker 이미지 빌드
├── docker-compose.yml         # app + db + sonarqube 컨테이너 구성
├── sonar-project.properties   # SonarQube 분석 설정
│
├── routers/                   # 라우터 레이어
│   ├── auth.py                # /auth/register, /auth/login
│   └── todos.py               # /todos CRUD + search
│
├── services/                  # 서비스 레이어 (비즈니스 로직)
│   ├── auth_service.py
│   └── todo_service.py
│
├── models/                    # Pydantic 스키마 & ORM 모델
│   ├── user.py
│   └── todo.py
│
├── core/                      # 공통 유틸리티
│   ├── security.py            # JWT 발급/검증, 비밀번호 해시
│   ├── database.py            # SQLAlchemy 엔진, 세션
│   └── config.py              # 환경변수 로딩 (pydantic Settings)
│
├── tests/                     # 테스트
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_ui_playwright.py
│   └── test_ui_selenium.py
│
├── static/                    # 정적 파일
│   ├── css/
│   └── js/
│
├── templates/                 # HTML 템플릿
│   └── index.html
│
└── docs/                      # 프로젝트 문서
    ├── 1-domain-definition.md
    ├── 2-prd.md
    ├── 3-user-scenario.md
    ├── 4-project-principle.md
    ├── 5-arc-diagram.md
    ├── 6-ERD.md
    ├── 7-execution-plan.md
    ├── 8-wireframe.md
    └── 9-APP-style-guide.md
```

---

## 7. 기술 스택

| 영역 | 기술 | 버전 | 선택 이유 |
|------|------|------|-----------|
| 백엔드 프레임워크 | FastAPI | 0.135 | 비동기, 자동 문서화, Pydantic 통합 |
| 인증 | python-jose + bcrypt | 최신 | JWT + bcrypt 해시 표준 라이브러리 |
| 데이터베이스 | PostgreSQL 15 | 15-alpine | 운영 환경 표준 RDBMS |
| ORM | SQLAlchemy | 2.0 | Python 표준 ORM |
| 프론트엔드 | HTML + Bootstrap 5 + Vanilla JS | - | 별도 빌드 없이 빠른 프로토타이핑 |
| 테스트 | pytest + httpx + Playwright + Selenium | 최신 | 통합·UI 테스트 커버리지 |
| 정적 분석 | SonarQube | latest | 코드 품질 게이트 |
| 컨테이너 | Docker + Docker Compose | - | 개발/운영 환경 통일 |
| CI/CD | Jenkins | - | 자동 빌드·테스트·배포 파이프라인 |
