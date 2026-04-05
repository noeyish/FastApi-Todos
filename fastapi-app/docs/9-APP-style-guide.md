# APP Style Guide — My TodoList v4

> 실제 적용된 CSS(`static/css/style.css`) 기준으로 작성된 디자인 시스템 문서

---

## 1. 색상 팔레트

### 기본 색상

| 토큰 | 값 | 용도 |
|---|---|---|
| `--bg` | `#F4F5F7` | 페이지 배경 |
| `--surface` | `#FFFFFF` | 카드, 모달, 입력창 배경 |
| `--border` | `#E8EAF0` | 테두리, 구분선 |

### 브랜드 색상

| 토큰 | 값 | 용도 |
|---|---|---|
| `--primary` | `#7A85FF` | 버튼, 포커스 테두리, 활성 탭, 배지 |
| `--primary-h` | `#6060FF` | 버튼 hover 상태 |

### 상태 색상

| 토큰 | 값 | 용도 |
|---|---|---|
| `--danger` | `#E5534B` | 기한 초과, 삭제 버튼 hover, 에러 |
| `--warning` | `#D97706` | 오늘 마감 |
| `--success` | `#16A34A` | 회원가입 버튼, 낮음 배지 |

### 텍스트 색상

| 토큰 | 값 | 용도 |
|---|---|---|
| `--text-1` | `#111827` | 본문, 제목 (기본 텍스트) |
| `--text-2` | `#6B7280` | 보조 텍스트, 라벨, placeholder |
| `--text-3` | `#9CA3AF` | 비활성, 아이콘, 완료된 항목 |

---

## 2. 타이포그래피

### 폰트

```
font-family: 'Inter', -apple-system, sans-serif;
```

- **Inter** (Google Fonts): 가독성 높은 모던 산세리프
- 폴백: macOS 시스템 폰트(`-apple-system`), 기타 sans-serif

### 크기 체계

| 용도 | 크기 | 굵기 |
|---|---|---|
| 페이지 타이틀 | `1.5rem` (24px) | 700 |
| 네비바 로고 | `1rem` (16px) | 700 |
| 버튼 (기본) | `0.9rem` (14.4px) | 600 |
| 할 일 제목 | `0.9rem` (14.4px) | 500 |
| 폼 라벨 | `0.8rem` (12.8px) | 500 |
| 배지 | `0.68rem` (10.9px) | 600 |
| 보조 텍스트 | `0.78rem` (12.5px) | 400 |
| 섹션 헤더 | `0.72rem` (11.5px) | 600 |

---

## 3. 간격 & 모서리

### 모서리 반경

| 토큰 | 값 | 용도 |
|---|---|---|
| `--radius` | `12px` | 카드, 모달, 인증 박스 |
| — | `10px` | Todo 카드 |
| — | `8px` | 버튼, 입력창 |
| — | `20px` | 필터/정렬 버튼, 배지, 섹션 헤더 |
| — | `6px` | 작은 요소 (모달 닫기, 에러) |

### 그림자

| 토큰 | 값 | 용도 |
|---|---|---|
| `--shadow-sm` | `0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04)` | 카드 기본, 탭 활성 |
| `--shadow` | `0 4px 16px rgba(0,0,0,.08)` | 카드 hover, 인증 박스 |
| 모달 전용 | `0 20px 60px rgba(0,0,0,.2)` | 모달 박스 |

---

## 4. 컴포넌트

### 버튼

| 종류 | 배경 | 텍스트 | 패딩 | 반경 |
|---|---|---|---|---|
| Primary (로그인) | `--primary` | `#fff` | `11px` (전체 너비) | `8px` |
| 추가 | `--primary` | `#fff` | `9px 18px` | `8px` |
| 로그아웃 | 투명 + 테두리 | `--text-2` | `6px 14px` | `8px` |
| 취소 | `--bg` + 테두리 | `--text-2` | `8px 16px` | `8px` |
| 저장 | `--primary` | `#fff` | `8px 20px` | `8px` |
| 아이콘 (수정/삭제) | 투명 | `--text-3` | `30×30px` | `7px` |

### 입력창

```
border: 1.5px solid --border
border-radius: 8px
padding: 10px 14px
outline: none
transition: border-color 0.15s
```
포커스 시: `border-color: --primary`

### Todo 카드

```
background: --surface
border: 1.5px solid --border
border-radius: 10px
padding: 14px 16px
box-shadow: --shadow-sm
```

**기한 상태별 스타일:**

| 상태 | 좌측 테두리 | 배경 |
|---|---|---|
| 기한 초과 | `3px solid #E5534B` | `#FFFAFA` |
| 오늘 마감 | `3px solid #D97706` | `#FFFDF5` |
| 예정 | `3px solid #7A85FF` | 기본 white |
| 완료 | 우선순위 색상 유지 | `opacity: 0.55` |

### 배지

| 종류 | 배경 | 텍스트 |
|---|---|---|
| 높음 | `#FEE2E2` | `#B91C1C` |
| 보통 | `#FEF3C7` | `#92400E` |
| 낮음 | `#D1FAE5` | `#065F46` |
| 기한 초과 | `#FEE2E2` | `#B91C1C` |
| 오늘 마감 | `#FEF3C7` | `#92400E` |
| 예정 날짜 | `#EEF2FF` + 테두리 `#C7D2FE` | `#4338CA` |

### 섹션 헤더

| 섹션 | 배경 | 텍스트 |
|---|---|---|
| 기한 초과 | `#FEE2E2` | `#B91C1C` |
| 오늘 마감 | `#FEF3C7` | `#92400E` |
| 예정 | `#DBEAFE` | `#1D4ED8` |
| 날짜 없음 | `#F3F4F6` | `#374151` |

---

## 5. 레이아웃

### 페이지 구조

```
┌──────────────────────────────────────┐
│         Topbar (56px, sticky)        │
├──────────────────────────────────────┤
│                                      │
│    main-body                         │
│    max-width: 640px                  │
│    margin: 0 auto                    │
│    padding: 28px 20px                │
│                                      │
└──────────────────────────────────────┘
```

### 인증 화면

```
display: flex / align-items: center / justify-content: center
min-height: 100vh
auth-box: max-width 380px
```

### 반응형

| 브레이크포인트 | 변경 사항 |
|---|---|
| `≤ 480px` | `add-meta` 줄바꿈, 패딩 `16px`로 축소 |

---

## 6. 인터랙션

| 요소 | 효과 | 전환 |
|---|---|---|
| Todo 카드 hover | `translateY(-1px)` + `--shadow` | `0.15s` |
| 버튼 hover | 배경색 변경 | `0.15s` |
| 탭/정렬 버튼 | 활성 색상 전환 | `0.15s ~ 0.2s` |
| 체크박스 | 커스텀 (`appearance: none`), 체크 시 `--primary` 채움 | `0.15s` |
| 모달 | 오버레이 클릭 시 닫힘, 배경 `rgba(0,0,0,.35)` | — |
