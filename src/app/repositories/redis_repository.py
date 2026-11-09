from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.redis import get_redis_db
from redis.asyncio import Redis
from fastapi import Depends
from sqlalchemy import insert, select, update, delete, func, exists



# repository에서 하면 안되는 것들:
# 1. 예외 처리(db에 접근하는 순수한 함수들로만 이루어져야 하므로)
class RedisRepository:
    # db가 필요
    # 생성자 주입(레포지토리가 호출되는 동시에 db 정보도 호출되어야 하므로 class가 호출될 때 자동으로 실행되는 생성자(init)에 db를 넣음)
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    # CRUD
    # 순수함수
    async def set(self, key: str, value: str, ex: int = 3600) -> None:
        await self.redis_client.set(key, value, ex)

    async def get(self, key: str) -> str | None:
        return await self.redis_client.get(key)
    
    async def exists(self, key: str) -> bool:
        result = await self.redis_client.exists(key)
        return result > 0
    
    async def delete(self, key: str) -> None:
        await self.redis_client.delete(key)


# 주입 팩토리 메서드
def get_redis_repository(redis_client: Redis = Depends(get_redis_db)):
    return RedisRepository(redis_client)

