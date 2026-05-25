from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from core.database import Base, engine
from routers import auth, todos
import os
import time
import logging
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text


# ── 로깅 설정 (콘솔 + Loki) ──────────────────────────────────
logger = logging.getLogger("fastapi-app")
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

LOKI_ENDPOINT = os.getenv("LOKI_ENDPOINT")
if LOKI_ENDPOINT:
    try:
        import logging_loki
        loki_handler = logging_loki.LokiHandler(
            url=LOKI_ENDPOINT,
            tags={"application": "fastapi-app"},
            version="1",
        )
        logger.addHandler(loki_handler)
        logger.info("Loki 핸들러 연결 완료: %s", LOKI_ENDPOINT)
    except Exception as exc:  # Loki 연결 실패해도 앱은 정상 동작
        logger.warning("Loki 핸들러 초기화 실패: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(text(
            "ALTER TABLE todos ADD COLUMN IF NOT EXISTS category VARCHAR DEFAULT 'general'"
        ))
        conn.commit()
    yield


app = FastAPI(title="My TodoList", lifespan=lifespan)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed_ms = round((time.time() - start) * 1000, 2)
    logger.info(
        "%s %s -> %s (%sms)",
        request.method, request.url.path, response.status_code, elapsed_ms,
    )
    return response


app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth.router)
app.include_router(todos.router)


@app.get("/health")
def health_check():
    db_ok = True
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        db_ok = False
        logger.error("헬스체크 DB 연결 실패: %s", exc)
    status = "ok" if db_ok else "degraded"
    return {"status": status, "database": "up" if db_ok else "down"}


@app.get("/", response_class=HTMLResponse)
def read_root():
    path = "templates/index.html"
    if not os.path.exists(path):
        return HTMLResponse("<h1>Todo App</h1>")
    with open(path, "r") as f:
        return HTMLResponse(f.read())
