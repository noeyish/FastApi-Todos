# 실행 계획 (Execution Plan)

> 기반 문서: `1-domain-definition.md`, `8-wireframe.md`
> 현재 상태: FastAPI + JSON 파일 저장, 인증 없음, due_date 없음
> 목표: 인증(회원가입/로그인) + DB 마이그레이션 + 계획완료일/기한초과 기능 추가

---

## 현재 구현 상태 (As-Is)

| 기능 | 상태 |
|------|------|
| 할 일 CRUD | ✅ 완료 |
| 우선순위(priority) | ✅ 완료 |
| 완료 상태 토글 | ✅ 완료 |
| 필터 탭 (전체/진행중/완료) | ✅ 완료 |
| 회원가입 / 로그인 | ❌ 미구현 |
| JWT 인증 | ❌ 미구현 |
| 계획 완료일(due_date) | ❌ 미구현 |
| 기한 초과 시각 구분 | ❌ 미구현 |
| 데이터베이스 (SQLite) | ❌ 미구현 (현재 JSON 파일) |

---

## 의존성 그래프

```
[DB-01] 환경/DB 설정
    └── [DB-02] User 테이블
            └── [BE-01] 회원가입 API
                    └── [BE-02] 로그인 / JWT 발급 API
                            └── [BE-03] JWT 인증 미들웨어
                                    └── [BE-04] Todo 모델 + API 마이그레이션
                                                └── [FE-01] 로그인/회원가입 페이지
                                                        └── [FE-02] JWT 클라이언트 처리
                                                                └── [FE-03] due_date UI + 기한초과 표시
```

---

## PHASE 1 — 데이터베이스 레이어

### DB-01. 개발 환경 및 DB 설정

**목표**: SQLite + SQLAlchemy 도입, JSON 파일 스토리지 대체

- [ ] `requirements.txt`에 의존성 추가
  - `sqlalchemy>=2.0`
  - `python-jose[cryptography]` (JWT)
  - `passlib[bcrypt]` (비밀번호 해시)
  - `python-multipart` (OAuth2 폼)
- [ ] `database.py` 생성: SQLite 엔진, SessionLocal, Base 정의
- [ ] `main.py`에서 앱 시작 시 `Base.metadata.create_all()` 호출

**완료 조건**:
- [ ] `uvicorn main:app` 실행 시 `todo.db` 파일 자동 생성
- [ ] 기존 JSON 엔드포인트가 여전히 동작함 (하위 호환)

---

### DB-02. 데이터베이스 모델 정의

**목표**: User, Todo ORM 모델 생성
**의존성**: DB-01 완료

- [ ] `models.py` 생성

**User 테이블**:
```
id          INTEGER  PK AUTOINCREMENT
email       TEXT     UNIQUE NOT NULL
hashed_pw   TEXT     NOT NULL
created_at  DATETIME DEFAULT now
```

**Todo 테이블**:
```
id          INTEGER  PK AUTOINCREMENT
user_id     INTEGER  FK → users.id  NOT NULL
title       TEXT     NOT NULL
description TEXT     DEFAULT ''
completed   BOOLEAN  DEFAULT FALSE
priority    TEXT     DEFAULT 'medium'   -- low | medium | high
due_date    DATE     NULLABLE
created_at  DATETIME DEFAULT now
```

**완료 조건**:
- [ ] `Base.metadata.create_all()` 실행 시 `users`, `todos` 테이블 생성 확인
- [ ] `user_id` FK 제약 조건 동작 확인

---

## PHASE 2 — 백엔드 레이어

### BE-01. 회원가입 API

**목표**: `POST /auth/register` 구현
**의존성**: DB-02 완료

- [ ] `schemas.py`에 `UserCreate`, `UserResponse` Pydantic 모델 정의
- [ ] `auth.py`에 `register` 엔드포인트 구현
  - 이메일 중복 체크 → 409 반환
  - `passlib`로 비밀번호 bcrypt 해시
  - DB에 User 저장
- [ ] `main.py`에 `auth` 라우터 포함 (`/auth` prefix)

**완료 조건**:
- [ ] `POST /auth/register` → 201, `UserResponse` 반환
- [ ] 중복 이메일 → 409 `{"detail": "이미 사용 중인 이메일입니다"}`
- [ ] DB에 비밀번호가 평문이 아닌 해시로 저장

---

### BE-02. 로그인 / JWT 발급 API

**목표**: `POST /auth/login` 구현, Access Token 발급
**의존성**: BE-01 완료

- [ ] `auth.py`에 `login` 엔드포인트 구현
  - 이메일/비밀번호 검증
  - `python-jose`로 JWT Access Token 생성 (만료: 60분)
- [ ] `config.py`에 `SECRET_KEY`, `ALGORITHM` 상수 정의

**완료 조건**:
- [ ] `POST /auth/login` → 200, `{"access_token": "...", "token_type": "bearer"}`
- [ ] 잘못된 자격증명 → 401 `{"detail": "이메일 또는 비밀번호가 올바르지 않습니다"}`
- [ ] JWT 페이로드에 `user_id`, `exp` 포함

---

### BE-03. JWT 인증 미들웨어

**목표**: 보호된 라우트에 JWT 검증 의존성 추가
**의존성**: BE-02 완료

- [ ] `dependencies.py`에 `get_current_user` 의존성 함수 구현
  - `Authorization: Bearer <token>` 헤더 파싱
  - 토큰 검증 → 만료/위변조 시 401 반환
  - DB에서 User 조회 반환
- [ ] Todo 관련 모든 엔드포인트에 `Depends(get_current_user)` 적용

**완료 조건**:
- [ ] 유효한 JWT 없이 `GET /todos` 요청 → 401
- [ ] 유효한 JWT로 `GET /todos` 요청 → 200 (해당 유저 데이터만)

---

### BE-04. Todo 모델 마이그레이션 및 API 수정

**목표**: JSON 파일 스토리지 → SQLite, `due_date` 필드 추가
**의존성**: BE-03 완료

- [ ] `TodoItem` Pydantic 모델에 `due_date: Optional[date]` 추가
- [ ] 모든 Todo CRUD 엔드포인트를 DB 기반으로 교체
  - `GET /todos` → 현재 유저의 Todo만 조회
  - `POST /todos` → `user_id` 자동 설정
  - `PUT /todos/{id}` → 본인 소유 Todo만 수정 가능 (타인 → 403)
  - `DELETE /todos/{id}` → 본인 소유 Todo만 삭제 가능 (타인 → 403)
  - `PATCH /todos/{id}/toggle` → 본인 소유 Todo만 토글 가능
- [ ] `todo.json` 의존 코드(`load_todos`, `save_todos`) 제거

**완료 조건**:
- [ ] 기존 5개 엔드포인트 모두 DB 기반으로 동작
- [ ] `due_date` 필드 저장/조회 정상 동작
- [ ] 타인의 Todo 접근 시 403 반환
- [ ] `todo.json` 파일 없어도 앱 정상 실행

---

## PHASE 3 — 프론트엔드 레이어

### FE-01. 회원가입 / 로그인 페이지

**목표**: 인증 UI 페이지 추가
**의존성**: BE-02 완료

- [ ] `templates/login.html` 생성
  - 이메일/비밀번호 폼
  - 비밀번호 보기/숨기기 토글 (👁 버튼)
  - 오류 메시지 표시 영역
  - "회원가입 하기" 링크
- [ ] `templates/register.html` 생성
  - 이메일/비밀번호/비밀번호 확인 폼
  - 비밀번호 불일치 클라이언트 검증
  - "로그인 하기" 링크
- [ ] `main.py`에 `GET /login`, `GET /register` 라우트 추가

**완료 조건**:
- [ ] `/login` 접속 시 로그인 페이지 렌더링
- [ ] `/register` 접속 시 회원가입 페이지 렌더링
- [ ] 비밀번호 불일치 시 제출 전 클라이언트 오류 표시

---

### FE-02. JWT 클라이언트 처리 및 인증 가드

**목표**: 토큰 저장/전송, 페이지 접근 제어
**의존성**: FE-01, BE-03 완료

- [ ] 로그인 성공 시 `localStorage`에 `access_token` 저장 후 `/` 리다이렉트
- [ ] `index.html`의 모든 API 요청에 `Authorization: Bearer <token>` 헤더 추가
- [ ] 페이지 로드 시 토큰 존재 여부 확인 → 없으면 `/login` 리다이렉트
- [ ] 401 응답 수신 시 토큰 삭제 후 `/login` 리다이렉트
- [ ] 로그아웃 버튼: `localStorage` 토큰 삭제 → `/login` 리다이렉트
- [ ] 네비바에 로그인 상태(사용자 이메일) 표시

**완료 조건**:
- [ ] 미인증 상태로 `/` 접근 시 `/login`으로 이동
- [ ] 로그인 후 모든 API 요청에 Bearer 토큰 포함
- [ ] 로그아웃 후 토큰이 localStorage에서 삭제됨

---

### FE-03. due_date UI 및 기한 초과 표시

**목표**: 계획 완료일 입력, 기한 상태별 시각 구분
**의존성**: FE-02, BE-04 완료

- [ ] 할 일 추가 폼에 `due_date` date picker 추가 (오늘 이전 날짜 비활성화)
- [ ] 할 일 수정 모달에 `due_date` 필드 추가
- [ ] `renderTodos()` 함수에서 기한 상태 계산 로직 추가:

```js
// 기한 상태 판별
function getDueDateStatus(due_date) {
  if (!due_date) return 'none';
  const today = new Date().toISOString().split('T')[0];
  if (due_date < today) return 'overdue';
  if (due_date === today) return 'today';
  return 'upcoming';
}
```

- [ ] 기한 상태별 카드 스타일 적용:
  - `overdue`: 배경 `#fff5f5`, 테두리 `#dc3545`, ⚠️ 아이콘 + "기한 초과: N일 전"
  - `today`: 배경 `#fffbf0`, 테두리 `#fd7e14`, 🔔 아이콘 + "오늘 마감"
  - `upcoming`: 우선순위 색상 테두리, 📅 날짜 표시
- [ ] 메인 목록을 "기한 초과 / 오늘 마감 / 예정" 섹션으로 그룹화하여 표시

**완료 조건**:
- [ ] 추가/수정 폼에서 due_date 저장 및 조회 정상 동작
- [ ] 기한 초과 항목 카드가 빨간 배경으로 표시
- [ ] 오늘 마감 항목 카드가 주황 배경으로 표시
- [ ] 완료된 항목은 기한 초과 스타일 미적용

---

## 전체 체크리스트 요약

### Phase 1 — Database
- [ ] DB-01: 환경/DB 설정
- [ ] DB-02: User + Todo ORM 모델

### Phase 2 — Backend
- [ ] BE-01: 회원가입 API
- [ ] BE-02: 로그인 / JWT 발급
- [ ] BE-03: JWT 인증 미들웨어
- [ ] BE-04: Todo 모델 마이그레이션 + due_date

### Phase 3 — Frontend
- [ ] FE-01: 로그인 / 회원가입 페이지
- [ ] FE-02: JWT 클라이언트 처리 + 인증 가드
- [ ] FE-03: due_date UI + 기한 초과 표시

---

## 파일 변경 영향 범위

| 파일 | 변경 유형 | 관련 Task |
|------|----------|----------|
| `requirements.txt` | 수정 | DB-01 |
| `database.py` | 신규 생성 | DB-01 |
| `models.py` | 신규 생성 | DB-02 |
| `schemas.py` | 신규 생성 | BE-01 |
| `config.py` | 신규 생성 | BE-02 |
| `auth.py` | 신규 생성 | BE-01, BE-02 |
| `dependencies.py` | 신규 생성 | BE-03 |
| `main.py` | 수정 (대폭) | DB-01, BE-04, FE-01 |
| `templates/index.html` | 수정 | FE-02, FE-03 |
| `templates/login.html` | 신규 생성 | FE-01 |
| `templates/register.html` | 신규 생성 | FE-01 |
| `todo.json` | 삭제 예정 | BE-04 |
