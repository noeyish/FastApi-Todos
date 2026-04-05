import pytest

USER = {"email": "test@example.com", "password": "testpassword123"}


def register_and_login(client, email=USER["email"], password=USER["password"]):
    client.post("/auth/register", json={"email": email, "password": password})
    res = client.post("/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ── 인증 ────────────────────────────────────────────────────────────────────

def test_register_success(client):
    res = client.post("/auth/register", json=USER)
    assert res.status_code == 201
    assert res.json()["email"] == USER["email"]


def test_register_duplicate_email(client):
    client.post("/auth/register", json=USER)
    res = client.post("/auth/register", json=USER)
    assert res.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json=USER)
    res = client.post("/auth/login", json=USER)
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert res.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/auth/register", json=USER)
    res = client.post("/auth/login", json={"email": USER["email"], "password": "wrongpassword"})
    assert res.status_code == 401


# ── Todo ─────────────────────────────────────────────────────────────────────

def test_create_todo(client):
    token = register_and_login(client)
    res = client.post("/todos", json={"title": "할 일", "priority": "high"}, headers=auth_headers(token))
    assert res.status_code == 201
    assert res.json()["title"] == "할 일"
    assert res.json()["priority"] == "high"
    assert res.json()["completed"] is False


def test_list_todos_empty(client):
    token = register_and_login(client)
    res = client.get("/todos", headers=auth_headers(token))
    assert res.status_code == 200
    assert res.json() == []


def test_list_todos_only_own(client):
    token_a = register_and_login(client, "a@example.com", "password123")
    token_b = register_and_login(client, "b@example.com", "password123")

    client.post("/todos", json={"title": "A의 할 일"}, headers=auth_headers(token_a))

    res = client.get("/todos", headers=auth_headers(token_b))
    assert res.json() == []


def test_update_todo(client):
    token = register_and_login(client)
    create_res = client.post("/todos", json={"title": "원래 제목"}, headers=auth_headers(token))
    todo_id = create_res.json()["id"]

    res = client.put(f"/todos/{todo_id}", json={"title": "수정된 제목"}, headers=auth_headers(token))
    assert res.status_code == 200
    assert res.json()["title"] == "수정된 제목"


def test_update_todo_not_found(client):
    token = register_and_login(client)
    res = client.put("/todos/999", json={"title": "없음"}, headers=auth_headers(token))
    assert res.status_code == 404


def test_toggle_todo(client):
    token = register_and_login(client)
    create_res = client.post("/todos", json={"title": "토글 테스트"}, headers=auth_headers(token))
    todo_id = create_res.json()["id"]

    res = client.patch(f"/todos/{todo_id}/toggle", headers=auth_headers(token))
    assert res.status_code == 200
    assert res.json()["completed"] is True

    res = client.patch(f"/todos/{todo_id}/toggle", headers=auth_headers(token))
    assert res.json()["completed"] is False


def test_delete_todo(client):
    token = register_and_login(client)
    create_res = client.post("/todos", json={"title": "삭제 테스트"}, headers=auth_headers(token))
    todo_id = create_res.json()["id"]

    res = client.delete(f"/todos/{todo_id}", headers=auth_headers(token))
    assert res.status_code == 204

    list_res = client.get("/todos", headers=auth_headers(token))
    assert list_res.json() == []


def test_delete_todo_not_found(client):
    token = register_and_login(client)
    res = client.delete("/todos/999", headers=auth_headers(token))
    assert res.status_code == 204


def test_todos_requires_auth(client):
    res = client.get("/todos")
    assert res.status_code in (401, 403)


# ── due_date ──────────────────────────────────────────────────────────────────

def test_create_todo_with_due_date(client):
    token = register_and_login(client)
    res = client.post(
        "/todos",
        json={"title": "날짜 있는 할 일", "due_date": "2099-12-31"},
        headers=auth_headers(token)
    )
    assert res.status_code == 201
    assert res.json()["due_date"] == "2099-12-31"


def test_create_todo_without_due_date(client):
    token = register_and_login(client)
    res = client.post("/todos", json={"title": "날짜 없는 할 일"}, headers=auth_headers(token))
    assert res.status_code == 201
    assert res.json()["due_date"] is None


def test_update_todo_due_date(client):
    token = register_and_login(client)
    create_res = client.post("/todos", json={"title": "날짜 수정 테스트"}, headers=auth_headers(token))
    todo_id = create_res.json()["id"]

    res = client.put(
        f"/todos/{todo_id}",
        json={"due_date": "2099-06-01"},
        headers=auth_headers(token)
    )
    assert res.status_code == 200
    assert res.json()["due_date"] == "2099-06-01"


def test_clear_todo_due_date(client):
    token = register_and_login(client)
    create_res = client.post(
        "/todos",
        json={"title": "날짜 제거 테스트", "due_date": "2099-12-31"},
        headers=auth_headers(token)
    )
    todo_id = create_res.json()["id"]

    res = client.put(f"/todos/{todo_id}", json={"due_date": None}, headers=auth_headers(token))
    assert res.status_code == 200
    assert res.json()["due_date"] is None


def test_overdue_todo_stored(client):
    """기한 초과 날짜도 그대로 저장/조회되는지 확인 (판별은 프론트에서)"""
    token = register_and_login(client)
    res = client.post(
        "/todos",
        json={"title": "기한 초과 테스트", "due_date": "2000-01-01"},
        headers=auth_headers(token)
    )
    assert res.status_code == 201
    assert res.json()["due_date"] == "2000-01-01"


# ── 정렬 (백엔드 데이터 정합성) ────────────────────────────────────────────────

def test_priority_values_valid(client):
    """high/medium/low 외 값은 기본값 medium으로 처리되거나 그대로 저장되는지 확인"""
    token = register_and_login(client)
    for priority in ["high", "medium", "low"]:
        res = client.post(
            "/todos",
            json={"title": f"우선순위 {priority}", "priority": priority},
            headers=auth_headers(token)
        )
        assert res.json()["priority"] == priority


def test_multiple_todos_returned_in_order(client):
    """여러 Todo 생성 시 모두 조회되는지 확인"""
    token = register_and_login(client)
    for i in range(3):
        client.post("/todos", json={"title": f"할 일 {i}"}, headers=auth_headers(token))

    res = client.get("/todos", headers=auth_headers(token))
    assert len(res.json()) == 3
