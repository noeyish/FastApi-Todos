"""
UI 테스트 — Playwright 4/9 테스트 v4.0.0
실행 전 서버가 실행 중이어야 합니다: uvicorn main:app --reload
실행: pytest tests/test_ui.py -v --headed   (브라우저 보이게)
      pytest tests/test_ui.py -v            (헤드리스)
"""
import os
import uuid
import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5001")
TEST_PASSWORD = "testpassword123"


def unique_email():
    return f"ui_{uuid.uuid4().hex[:8]}@example.com"


# ── 헬퍼 ──────────────────────────────────────────────────────────────────────

def do_register(page: Page, email=None, password=TEST_PASSWORD):
    email = email or unique_email()
    page.goto(BASE_URL)
    page.click("text=회원가입")
    page.fill("#reg-email", email)
    page.fill("#reg-password", password)
    page.click("button.btn-primary.green")
    page.wait_for_selector(".topbar-logo")


def do_login(page: Page, email=None, password=TEST_PASSWORD):
    email = email or unique_email()
    page.goto(BASE_URL)
    page.fill("#login-email", email)
    page.fill("#login-password", password)
    page.click("#login-form button[type='submit']")
    page.wait_for_selector(".topbar-logo")


# ── 인증 UI ───────────────────────────────────────────────────────────────────

def test_auth_page_loads(page: Page):
    """접속 시 인증 화면이 표시된다"""
    page.goto(BASE_URL)
    expect(page.locator(".auth-logo h1")).to_contain_text("To-Do List")
    expect(page.locator("#login-form")).to_be_visible()


def test_register_tab_switch(page: Page):
    """회원가입 탭 클릭 시 회원가입 폼이 표시된다"""
    page.goto(BASE_URL)
    page.click("text=회원가입")
    expect(page.locator("#register-form")).to_be_visible()
    expect(page.locator("#login-form")).to_be_hidden()


def test_login_wrong_password_shows_error(page: Page):
    """잘못된 비밀번호 입력 시 에러 메시지가 표시된다"""
    page.goto(BASE_URL)
    page.fill("#login-email", "nobody@example.com")
    page.fill("#login-password", "wrongpassword")
    page.click("#login-form button[type='submit']")
    expect(page.locator("#auth-error")).to_be_visible()


def test_register_and_auto_login(page: Page):
    """회원가입 후 자동 로그인되어 메인 화면이 표시된다"""
    do_register(page)
    expect(page.locator(".topbar-logo")).to_be_visible()
    expect(page.locator(".add-card")).to_be_visible()


def test_logout(page: Page):
    """로그아웃 클릭 시 인증 화면으로 돌아간다"""
    do_register(page)
    page.click(".btn-logout")
    expect(page.locator("#auth-section")).to_be_visible()


# ── Todo UI ───────────────────────────────────────────────────────────────────

def test_create_todo(page: Page):
    """할 일 추가 후 목록에 표시된다"""
    do_register(page)
    page.fill("#title", "UI 테스트 할 일")
    page.click(".btn-add")
    expect(page.locator(".todo-card").first).to_contain_text("UI 테스트 할 일")


def test_create_todo_with_priority(page: Page):
    """우선순위 높음으로 추가하면 높음 배지가 표시된다"""
    do_register(page)
    page.fill("#title", "긴급 처리")
    page.select_option("#priority", "high")
    page.click(".btn-add")
    expect(page.locator(".badge-high").first).to_be_visible()


def test_create_todo_with_due_date(page: Page):
    """완료일 지정 후 추가하면 날짜 배지가 표시된다"""
    do_register(page)
    page.fill("#title", "날짜 있는 할 일")
    page.fill("#due_date", "2099-12-31")
    page.click(".btn-add")
    expect(page.locator(".badge-upcoming").first).to_contain_text("2099-12-31")


def test_toggle_todo(page: Page):
    """체크박스 클릭 시 완료 처리된다"""
    do_register(page)
    page.fill("#title", "완료할 할 일")
    page.click(".btn-add")
    page.locator(".todo-check").first.click()
    expect(page.locator(".todo-card.done").first).to_be_visible()


def test_delete_todo(page: Page):
    """삭제 후 목록에서 제거된다"""
    do_register(page)
    page.fill("#title", "삭제할 할 일")
    page.click(".btn-add")
    page.wait_for_selector(".todo-card")

    page.on("dialog", lambda d: d.accept())
    page.locator(".btn-icon.del").first.click()
    expect(page.locator(".empty-state")).to_be_visible()


def test_filter_active(page: Page):
    """진행 중 필터 클릭 시 완료된 항목이 숨겨진다"""
    do_register(page)
    page.fill("#title", "완료 항목")
    page.click(".btn-add")
    page.locator(".todo-check").first.click()

    page.fill("#title", "진행 중 항목")
    page.click(".btn-add")

    page.click("button.filter-btn:text('진행 중')")
    expect(page.locator(".todo-card")).to_have_count(1)
    expect(page.locator(".todo-card").first).to_contain_text("진행 중 항목")


def test_sort_by_priority(page: Page):
    """우선순위 정렬 클릭 시 높음이 먼저 표시된다"""
    do_register(page)
    page.fill("#title", "낮은 우선순위")
    page.select_option("#priority", "low")
    page.click(".btn-add")
    page.wait_for_selector(".todo-card:has-text('낮은 우선순위')")

    page.fill("#title", "높은 우선순위")
    page.select_option("#priority", "high")
    page.click(".btn-add")
    page.wait_for_selector(".todo-card:has-text('높은 우선순위')")

    page.click("button.sort-btn:text('우선순위')")
    first_card = page.locator(".todo-card").first
    expect(first_card).to_contain_text("높은 우선순위")
