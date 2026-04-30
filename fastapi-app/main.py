from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from core.database import Base, engine
from routers import auth, todos
import os
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text


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

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth.router)
app.include_router(todos.router)


@app.get("/", response_class=HTMLResponse)
def read_root():
    path = "templates/index.html"
    if not os.path.exists(path):
        return HTMLResponse("<h1>Todo App</h1>")
    with open(path, "r") as f:
        return HTMLResponse(f.read())
