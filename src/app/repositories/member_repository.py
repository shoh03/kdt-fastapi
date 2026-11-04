from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.postgresql import get_postgresql_db
from fastapi import Depends

# 모델, ORM
from app.models.member_model import Member
from app.schemas.member_schema import (
    MemberCreateDTO, MemberClaimDTO, MemberUpdateDTO
)
from sqlalchemy import insert, select, update, delete, func, exists  # CRUD 순서

class MemberRepository:
    # db가 필요
    # 생성자 주입(레포지토리가 호출되는 동시에 db 정보도 호출되어야 하므로 함수가 실행될 때 자동으로 실행되는 생성자(init)에 db를 넣음)
    def __init__(self, db:AsyncSession):
        self.db = db



# 순수함수
# 1. 이메일 중복 확인
    async def exists_member_by_id(self, id: int) -> bool:
        query = (
            select(exists().where(Member.id == id))
        )
        result = await self.db.execute(query)
        return result.scalar()


    async def exists_member_email_and_provider(self, member_email: str, member_provider: str) -> bool:
        query = select(Member).where(
            Member.member_email == member_email,
            Member.member_provider == member_provider,
        )  # 이메일과 provider을 같이 비교(ex - email = shoh03, provider = GOOGLE)

        result = await self.db.execute(query)
        found_member = result.scalar_one_or_none()
        return found_member is not None

    # 2. 회원가입
    async def create_member(self, member: MemberCreateDTO):
        # pydantic -> dict
        new_member = member.model_dump()
        query = (
            insert(Member)
            .values(**new_member)
        ).returning(
            Member.id,
            Member.member_email,
            Member.member_provider
        )

        result = await self.db.execute(query)
        await self.db.commit()

        # 필요한 값을 리턴(id, email, provider)
        id, member_email, member_provider = result.first()

        payload = {
            "id": id,
            "member_email": member_email,
            "member_provider": member_provider
        }

        # dict -> pydantic
        claim_dto = MemberClaimDTO.model_validate(payload)
        return claim_dto


    # 3. 소셜 회원가입
    # 4. 회원 정보 조회(id)
    async def find_member_by_id(self, id: int):
        query = select(Member).where(Member.id == id)
        result = await self.db.execute(query)
        found_member = result.scalar_one_or_none()
        return found_member

    # 5. 회원 정보 조회(email, provider)
    async def find_member_by_email_provider(self, email: str, provider: str):
        query = select(Member).where(Member.member_email == email and Member.member_provider == provider)
        result = await self.db.execute(query)
        found_member = result.scalar_one_or_none()
        return found_member

    # 6. 회원 전체 정보 조회
    async def find_all_members(self) -> list[Member]:
        query = select(Member)
        result = await self.db.execute(query)
        found_members = result.scalars().all()
        return found_members

    # 6-1. 회원 전체 정보 조회(실무) + 페이지네이션
    # offset - limit
    # page - perpage
    async def find_member_by_paging(self, offset: int, limit: int) -> list[Member]:
        query = (
            select(Member)
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def count_members(self) -> int:
        query = (
            select(func.count()).select_from(Member)
        )
        result = await self.db.execute(query)
        count = result.scalar_one()
        return count

    # 7. 회원 정보 수정
    async def update_member(self, id: int, update_data: dict) -> Member | None:
        if not update_data:
            return None

        # 업데이트 시 None 제외
        query = (
            update(Member)
            .where(Member.id == id)
            .values(**update_data)
            .returning(Member)
        )

        result = await self.db.execute(query)
        await self.db.commit()

        updated_member = result.scalar_one_or_none()
        return updated_member


    # 8. 회원 삭제
    async def delete_member(self, id: int):
        query = (
            delete(Member)
                .where(Member.id == id)
        )

        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0



# 주입 팩토리 메서드
def get_member_repository(db: AsyncSession = Depends(get_postgresql_db)):
    return MemberRepository(db)