from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.postgresql import get_postgresql_db
from fastapi import Depends
from sqlalchemy import insert, select, update, delete, func, exists



# repository에서 하면 안되는 것들:
# 1. 예외 처리(db에 접근하는 순수한 함수들로만 이루어져야 하므로)
class DefaultRepository:
    # db가 필요
    # 생성자 주입(레포지토리가 호출되는 동시에 db 정보도 호출되어야 하므로 class가 호출될 때 자동으로 실행되는 생성자(init)에 db를 넣음)
    def __init__(self, db:AsyncSession):
        self.db = db

    # 순수함수

# 주입 팩토리 메서드
def get_default_repository(db: AsyncSession = Depends(get_postgresql_db)):
    return DefaultRepository(db)

