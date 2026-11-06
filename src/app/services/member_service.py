from fastapi import Depends, HTTPException
from app.repositories.member_repository import MemberRepository, get_member_repository
from app.models.member_model import Member
from app.schemas.member_schema import (
    MemberCreateDTO, MemberClaimDTO, MemberResponseDTO, MemberUpdateDTO
)
from app.utils.security_util import get_password_hash
import math 

from app.schemas.common_schema import PageResponseDTO

# 예외처리, 서비스가 들어나도록 이름을 선정해서 제작
# 트랜잭션 관리
class MemberService:

    def __init__(self, repo: MemberRepository):
        self.repo = repo

    # 회원 이메일 중복확인
    async def check_duplicate_member(self, member_email: str, member_provider: str) -> None:
        result = await self.repo.exists_member_email_and_provider(member_email, member_provider)
    
        if result:
            raise HTTPException(
                status_code=409,
                detail="이미 존재하는 이메일입니다"
            )

    # 로컬 회원 가입
    async def join(self, member: MemberCreateDTO) -> MemberClaimDTO:
        # 중복확인
        await self.check_duplicate_member(member.member_email, member.member_provider)

        # 알고리즘
        # 비밀번호 암호화
        encrypted_password = get_password_hash(member.member_password)

        # 암호화된 비밀번호로 변경
        new_member = MemberCreateDTO(
            **member.model_dump(exclude={"member_password"}),
            member_password = encrypted_password
        )
        # member_password = encrypted_password -> 이런식으로 원래 password 값에 덮어쓰기 금지

        return await self.repo.create_member(new_member)
        # 이메일, 비밀번호, 이름, 나이, 휴대폰 번호, ... 입력 받아 db에 저장


    # 회원조회
    async def get_member_by_id(self, id: int):
        found_member = await self.repo.find_member_by_id(id)

        if not found_member:
            raise HTTPException(
                status_code=404,
                detail="회원이 존재하지 않습니다."
            )

        return MemberResponseDTO.model_validate(found_member)

    # 회원조회(email, provider)
    async def get_member_by_email_provider(self, email: str, provider: str) -> MemberResponseDTO:
        found_member = await self.repo.find_member_by_email_provider(email, provider)

        if not found_member:
            raise HTTPException(
                status_code=404,
                detail="회원이 존재하지 않습니다."
            )

        return MemberResponseDTO.model_validate(found_member)

    # 전체 회원 조회
    async def get_all_members(self) -> list[MemberResponseDTO]:
        found_members = await self.repo.find_all_members()
        if not found_members:
            raise HTTPException(
                status_code=404,
                detail="회원이 비어있습니다."
            )

        return [MemberResponseDTO.model_validate(member) for member in found_members]

    # 회원전체조회 + 페이지네이션
    async def get_member_paging(self, offset: int, limit: int) -> PageResponseDTO:
        current_page = offset
        offset = (offset - 1) * limit

        total_count = await self.repo.count_members()
        members = await self.repo.find_member_by_paging(offset, limit)
        total_pages = math.ceil(total_count / limit)
        items_dto = [MemberResponseDTO.model_validate(member) for member in members]

        return PageResponseDTO(
            total_count=total_count,
            total_page=total_pages,
            offset=current_page,
            limit=limit,
            items=items_dto
        )

    # 회원 정보 수정
    async def update_member(self, id: int, member: MemberUpdateDTO):

        exist_member = await self.repo.exists_member_by_id(id)
        if not exist_member:
            raise HTTPException(detail="회원을 찾을 수 없습니다.", status_code= 404)

        # dto -> dict
        # exclude_unset=True: None컬럼 모두 제거
        update_data = member.model_dump(exclude_unset=True)

        if "member_password" in update_data and update_data["member_password"]:
            update_data["member_password"] = get_password_hash(update_data["member_password"])

        # dict -> dto
        updated_member = await self.repo.update_member(id, update_data)

        # 비밀번호 제거
        response_member = MemberResponseDTO.model_validate(updated_member)
        return response_member

    async def withdraw(self, id: int):
        is_deleted = await self.repo.delete_member(id)

        if not is_deleted:
            raise HTTPException(
                status_code=404,
                detail="회원이 존재하지 않습니다"
            )

    

# 레포지토리 주입 팩토리 함수
def get_member_service(repo: MemberRepository = Depends(get_member_repository)):
    return MemberService(repo)