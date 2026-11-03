# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routers import auth, subjects


@asynccontextmanager
async def lifespan(app: FastAPI):
    # fail fast: если БД недоступна — приложение не стартует
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    yield
    engine.dispose()


app = FastAPI(title="Study Planner API", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(subjects.router)


@app.get("/health")
def health():
    return {"status": "ok"}