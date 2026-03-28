from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from core.database import Base, engine
from routers import auth, todos
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="My TodoList")

app.include_router(auth.router)
app.include_router(todos.router)


@app.get("/", response_class=HTMLResponse)
def read_root():
    path = "templates/index.html"
    if not os.path.exists(path):
        return HTMLResponse("<h1>Todo App</h1>")
    with open(path, "r") as f:
        return HTMLResponse(f.read())
