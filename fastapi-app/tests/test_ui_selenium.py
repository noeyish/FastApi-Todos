"""
UI 테스트 — Selenium
실행 전 서버가 실행 중이어야 합니다: docker compose up -d
실행: pytest tests/test_ui_selenium.py -v --html=tests/selenium-report.html --self-contained-html

[Playwright vs Selenium 비교]
- Playwright : MCP 연동, CDP 직접 통신, auto-wait, 빠름
- Selenium   : WebDriver 프로토콜, 명시적 대기(WebDriverWait) 필요, 업계 표준
"""
import os
import uuid
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5001")
TEST_PASSWORD = "testpassword123"
WAIT = 10  # 최대 대기 시간(초) — Playwright의 auto-wait에 대응


def unique_email():
    return f"sel_{uuid.uuid4().hex[:8]}@example.com"


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")
    drv = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


def wait_for(driver, by, selector, timeout=WAIT):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, selector))
    )


# ── 헬퍼 ──────────────────────────────────────────────────────────────────────

def do_register(driver, email=None, password=TEST_PASSWORD):
    email = email or unique_email()
    driver.get(BASE_URL)
    wait_for(driver, By.CSS_SELECTOR, ".auth-tab-btn")
    driver.find_elements(By.CSS_SELECTOR, ".auth-tab-btn")[1].click()
    wait_for(driver, By.ID, "reg-email")
    driver.find_element(By.ID, "reg-email").send_keys(email)
    driver.find_element(By.ID, "reg-password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button.btn-primary.green").click()
    wait_for(driver, By.CSS_SELECTOR, ".topbar-logo")
    return email


def do_login(driver, email, password=TEST_PASSWORD):
    driver.get(BASE_URL)
    wait_for(driver, By.ID, "login-email")
    driver.find_element(By.ID, "login-email").send_keys(email)
    driver.find_element(By.ID, "login-password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "#login-form button[type='submit']").click()
    wait_for(driver, By.CSS_SELECTOR, ".topbar-logo")


# ── 인증 UI ───────────────────────────────────────────────────────────────────

def test_auth_page_loads(driver):
    """접속 시 인증 화면이 표시된다"""
    driver.get(BASE_URL)
    logo = wait_for(driver, By.CSS_SELECTOR, ".auth-logo h1")
    assert "To-Do List" in logo.text
    assert driver.find_element(By.ID, "login-form").is_displayed()


def test_register_tab_switch(driver):
    """회원가입 탭 클릭 시 회원가입 폼이 표시된다"""
    driver.get(BASE_URL)
    wait_for(driver, By.CSS_SELECTOR, ".auth-tab-btn")
    driver.find_elements(By.CSS_SELECTOR, ".auth-tab-btn")[1].click()
    wait_for(driver, By.ID, "register-form")
    assert driver.find_element(By.ID, "register-form").is_displayed()


def test_login_wrong_password_shows_error(driver):
    """잘못된 비밀번호 입력 시 에러 메시지가 표시된다"""
    driver.get(BASE_URL)
    wait_for(driver, By.ID, "login-email")
    driver.find_element(By.ID, "login-email").send_keys("nobody@example.com")
    driver.find_element(By.ID, "login-password").send_keys("wrongpassword")
    driver.find_element(By.CSS_SELECTOR, "#login-form button[type='submit']").click()
    wait_for(driver, By.ID, "auth-error")
    assert driver.find_element(By.ID, "auth-error").is_displayed()


def test_register_and_auto_login(driver):
    """회원가입 후 자동 로그인되어 메인 화면이 표시된다"""
    do_register(driver)
    assert driver.find_element(By.CSS_SELECTOR, ".topbar-logo").is_displayed()
    assert driver.find_element(By.CSS_SELECTOR, ".add-card").is_displayed()


def test_logout(driver):
    """로그아웃 클릭 시 인증 화면으로 돌아간다"""
    do_register(driver)
    driver.find_element(By.CSS_SELECTOR, ".btn-logout").click()
    wait_for(driver, By.ID, "auth-section")
    assert driver.find_element(By.ID, "auth-section").is_displayed()


# ── Todo UI ───────────────────────────────────────────────────────────────────

def test_create_todo(driver):
    """할 일 추가 후 목록에 표시된다"""
    do_register(driver)
    driver.find_element(By.ID, "title").send_keys("Selenium 테스트 할 일")
    driver.find_element(By.CSS_SELECTOR, ".btn-add").click()
    card = wait_for(driver, By.CSS_SELECTOR, ".todo-card")
    assert "Selenium 테스트 할 일" in card.text


def test_create_todo_with_priority(driver):
    """우선순위 높음으로 추가하면 높음 배지가 표시된다"""
    do_register(driver)
    driver.find_element(By.ID, "title").send_keys("긴급 처리")
    Select(driver.find_element(By.ID, "priority")).select_by_value("high")
    driver.find_element(By.CSS_SELECTOR, ".btn-add").click()
    wait_for(driver, By.CSS_SELECTOR, ".badge-high")
    assert driver.find_element(By.CSS_SELECTOR, ".badge-high").is_displayed()


def test_create_todo_with_due_date(driver):
    """완료일 지정 후 추가하면 날짜 배지가 표시된다"""
    do_register(driver)
    driver.find_element(By.ID, "title").send_keys("날짜 있는 할 일")
    driver.execute_script(
        "document.getElementById('due_date').value = '2099-12-31'"
    )
    driver.find_element(By.CSS_SELECTOR, ".btn-add").click()
    badge = wait_for(driver, By.CSS_SELECTOR, ".badge-upcoming")
    assert "2099-12-31" in badge.text


def test_toggle_todo(driver):
    """체크박스 클릭 시 완료 처리된다"""
    do_register(driver)
    driver.find_element(By.ID, "title").send_keys("완료할 할 일")
    driver.find_element(By.CSS_SELECTOR, ".btn-add").click()
    wait_for(driver, By.CSS_SELECTOR, ".todo-check")
    driver.find_element(By.CSS_SELECTOR, ".todo-check").click()
    wait_for(driver, By.CSS_SELECTOR, ".todo-card.done")
    assert driver.find_element(By.CSS_SELECTOR, ".todo-card.done").is_displayed()


def test_delete_todo(driver):
    """삭제 후 목록에서 제거된다"""
    do_register(driver)
    driver.find_element(By.ID, "title").send_keys("삭제할 할 일")
    driver.find_element(By.CSS_SELECTOR, ".btn-add").click()
    wait_for(driver, By.CSS_SELECTOR, ".btn-icon.del")
    driver.execute_script("window.confirm = () => true")
    driver.find_element(By.CSS_SELECTOR, ".btn-icon.del").click()
    wait_for(driver, By.CSS_SELECTOR, ".empty-state")
    assert driver.find_element(By.CSS_SELECTOR, ".empty-state").is_displayed()


def test_filter_active(driver):
    """진행 중 필터 클릭 시 완료된 항목이 숨겨진다"""
    do_register(driver)

    driver.find_element(By.ID, "title").send_keys("완료 항목")
    driver.find_element(By.CSS_SELECTOR, ".btn-add").click()
    wait_for(driver, By.CSS_SELECTOR, ".todo-check")
    driver.find_element(By.CSS_SELECTOR, ".todo-check").click()
    wait_for(driver, By.CSS_SELECTOR, ".todo-card.done")

    driver.find_element(By.ID, "title").send_keys("진행 중 항목")
    driver.find_element(By.CSS_SELECTOR, ".btn-add").click()
    WebDriverWait(driver, WAIT).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, ".todo-card")) == 2
    )

    btns = driver.find_elements(By.CSS_SELECTOR, ".filter-btn")
    for btn in btns:
        if "진행 중" in btn.text:
            btn.click()
            break

    WebDriverWait(driver, WAIT).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, ".todo-card")) == 1
    )
    cards = driver.find_elements(By.CSS_SELECTOR, ".todo-card")
    assert len(cards) == 1
    assert "진행 중 항목" in cards[0].text


def test_sort_by_priority(driver):
    """우선순위 정렬 클릭 시 높음이 먼저 표시된다"""
    do_register(driver)

    driver.find_element(By.ID, "title").send_keys("낮은 우선순위")
    Select(driver.find_element(By.ID, "priority")).select_by_value("low")
    driver.find_element(By.CSS_SELECTOR, ".btn-add").click()
    WebDriverWait(driver, WAIT).until(
        lambda d: any("낮은 우선순위" in c.text for c in d.find_elements(By.CSS_SELECTOR, ".todo-card"))
    )

    driver.find_element(By.ID, "title").send_keys("높은 우선순위")
    Select(driver.find_element(By.ID, "priority")).select_by_value("high")
    driver.find_element(By.CSS_SELECTOR, ".btn-add").click()
    WebDriverWait(driver, WAIT).until(
        lambda d: any("높은 우선순위" in c.text for c in d.find_elements(By.CSS_SELECTOR, ".todo-card"))
    )

    btns = driver.find_elements(By.CSS_SELECTOR, ".sort-btn")
    for btn in btns:
        if "우선순위" in btn.text:
            btn.click()
            break

    first_card = WebDriverWait(driver, WAIT).until(
        lambda d: d.find_elements(By.CSS_SELECTOR, ".todo-card")[0]
    )
    assert "높은 우선순위" in first_card.text
