# 설정의 책임 분리 (Separation of Concerns)

import os
from dotenv import load_dotenv
import redis.asyncio as redis
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    encoding="utf-8",
    decode_responses=True
)

@asynccontextmanager
async def start_redis_client(app: FastAPI):
    try:
        app.state.redis = redis_client
        yield
        
    finally:
        await app.state.redis.close()

def get_redis_db(request: Request):
    return request.app.state.redis