from fastapi import FastAPI
from app.security.cors import setup_cors
from app.security.security_headers import set_up_security
from contextlib import asynccontextmanager
from app.infrastructure.postgresql import engine, Base
from app.infrastructure.redis import start_redis_client
import app.models  # model 폴더의 init에서 import된 모든 모델들을 코드 한 줄만으로 가져옴.
from app.apis import member_api, post_api, auth_api


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 비동기 연결
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("PostgreSQL 연결 성공")

    async with start_redis_client(app):
        print("Redis 연결 성공")

        yield

app = FastAPI(
    lifespan=lifespan,
    title="Fast API Service",
    description="파이썬 백엔드 구축",
    version="1.0.0",
    docs_url="/docs",  # Swagger(API를 만들면 자동으로 해당하는 문서를 만들고 테스트할 수 있게 해줌)
    redoc_url="/redoc"
)

setup_cors(app)
set_up_security(app)

@app.get("/")
def health_check():
    return {"message": "hello, world"}

app.include_router(member_api.router, prefix="/members", tags=["members"])
app.include_router(post_api.router, prefix="/posts", tags=["posts"])
app.include_router(auth_api.router, prefix="/auth", tags=["auth"])