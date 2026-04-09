# 실행 계획 (Execution Plan)
## My TodoList 앱 — v5.0.0

> 기반 문서: `1-domain-definition.md`, `2-prd.md`, `8-wireframe.md`

---

## 버전별 구현 이력

| 버전 | 주요 내용 |
|------|---------|
| v3.0.0 | FastAPI + SQLite → PostgreSQL 전환, JWT 인증, Todo CRUD, 기한 초과 UI |
| v4.0.0 | 필터(전체/진행중/완료), 우선순위 정렬, Docker 배포, Jenkins CI/CD |
| v4.1.0 | Playwright UI 테스트, Selenium UI 테스트, SonarQube 환경 구성, 릴리즈 노트 템플릿 |
| **v5.0.0** | **검색 기능, 통계 대시보드, 인라인 수정 UI** |

---

## 현재 구현 상태 (v4.1 기준 As-Is)

| 기능 | 상태 |
|------|------|
| 회원가입 / 로그인 (JWT) | ✅ 완료 |
| 할 일 CRUD | ✅ 완료 |
| 우선순위 (low/medium/high) | ✅ 완료 |
| 완료 상태 토글 | ✅ 완료 |
| 기한 초과 시각 구분 | ✅ 완료 |
| 필터 탭 (전체/진행중/완료) | ✅ 완료 |
| 우선순위 정렬 | ✅ 완료 |
| PostgreSQL 연동 | ✅ 완료 |
| Docker + docker-compose | ✅ 완료 |
| Jenkins CI/CD | ✅ 완료 |
| Playwright UI 테스트 (12개) | ✅ 완료 |
| Selenium UI 테스트 (12개) | ✅ 완료 |
| SonarQube 환경 구성 | ✅ 완료 |
| **할 일 검색** | ✅ 완료 |
| **통계 대시보드** | ❌ 미구현 |
| **인라인 수정 UI** | ✅ 완료 |

---

## v5 구현 계획

### FE-01. 검색 기능 ✅

**목표**: 제목 키워드로 실시간 필터링
**변경 범위**: `templates/index.html`, `static/js/app.js`, `static/css/style.css`

- [x] 검색창 + 검색 버튼 UI 추가 (할 일 목록 상단)
- [x] `oninput` 이벤트로 실시간 필터링, Enter/버튼 클릭도 지원
- [x] 클라이언트 사이드 필터링 (`allTodos` 메모리에서 즉시 처리)
- [x] 검색어 있을 때 ✕ 버튼 표시 → 클릭 시 초기화
- [x] 검색 결과 개수 안내 (`'키워드' 검색 결과 N개`)
- [x] 기존 필터(전체/진행중/완료)와 AND 조건으로 동시 적용

**완료 조건**:
- [x] 키워드 입력 즉시 목록 필터링
- [x] 검색어 삭제 시 전체 목록 복원
- [x] 대소문자 구분 없이 검색

---

### FE-02. 통계 대시보드

**목표**: 완료율 및 개수 현황 표시
**변경 범위**: `templates/index.html`

- [ ] 메인 페이지 상단에 통계 카드 영역 추가
  ```
  [전체: N] [완료: N] [진행 중: N] [완료율: N%]
  ```
- [ ] `renderStats()` 함수 구현 — fetchTodos 완료 후 호출
- [ ] 할 일 추가/완료/삭제 시 통계 자동 갱신

**완료 조건**:
- [ ] 완료율이 % 단위로 표시됨
- [ ] 할 일 상태 변경 즉시 수치 업데이트

---

### FE-03. 인라인 수정 UI ✅

**목표**: 카드에서 바로 제목 수정
**변경 범위**: `static/js/app.js`, `static/css/style.css`

- [x] 카드 제목 텍스트 hover 시 배경 강조 (수정 가능 힌트)
- [x] 제목 클릭 시 인라인 `<input>` 전환 (`startInlineEdit()`)
- [x] Enter / blur 시 `PUT /todos/{id}` API 호출 후 목록 갱신
- [x] ESC 키 시 편집 취소, 원래 텍스트 복원
- [x] 완료된 항목은 인라인 수정 비활성화

**완료 조건**:
- [x] 수정 후 목록 즉시 업데이트
- [x] ESC로 취소 시 원래 값 복원

---

### TEST-01. v5 테스트 추가

**목표**: 신규 기능 테스트 케이스 추가
**변경 범위**: `tests/test_ui_playwright.py`, `tests/test_ui_selenium.py`

- [ ] `test_search_todo` — 검색어 입력 시 필터링 동작 검증
- [ ] `test_stats_update` — 완료 처리 후 완료율 변경 검증
- [ ] `test_inline_edit` — 인라인 수정 후 내용 반영 검증

---

## 전체 v5 체크리스트

### Frontend
- [x] FE-01: 검색 기능
- [ ] FE-02: 통계 대시보드
- [x] FE-03: 인라인 수정 UI

### Test
- [ ] TEST-01: 신규 기능 테스트 추가 (검색, 인라인 수정)

### Docs
- [x] 문서 전체 업데이트 (v5 기준)
- [ ] 릴리즈 노트 작성 (`docs/release-note-v5.0.0.md`)
- [ ] GitHub Release 태그 생성 (`v5.0.0`)

---

## 파일 변경 영향 범위

| 파일 | 변경 유형 | 관련 Task |
|------|----------|----------|
| `templates/index.html` | 수정 | FE-01, FE-02, FE-03 |
| `static/js/` | 수정 (있을 경우) | FE-01, FE-02, FE-03 |
| `tests/test_ui_playwright.py` | 수정 | TEST-01 |
| `tests/test_ui_selenium.py` | 수정 | TEST-01 |
| `docs/release-note-v5.0.0.md` | 신규 | - |
