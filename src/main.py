from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.infrastructure.postgresql import engine, Base

async def lifespan(app: FastAPI):
    # 비동기 연결
    async with engine.begin() as conn:
        pass

    yield

app = FastAPI(
    title="Fast API Service",
    description="파이썬 백엔드 구축",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
def health_check():
    return {"message": "hello, world"}