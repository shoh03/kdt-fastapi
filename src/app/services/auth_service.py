import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from app.repositories.redis_repository import get_redis_repository, RedisRepository
from app.services.member_service import get_member_service, MemberService
from app.utils.security_util import verify_password
from app.utils.jwt_token_util import (
    parse_token, generate_access_token, generate_refresh_token, reissue_access_token
)
from app.schemas.auth_schema import JwtTokenDTO, LoginRequestDTO, SocialLoginRequestDTO
from app.schemas.member_schema import MemberClaimDTO

load_dotenv()
TOKEN_BLACKLIST_PREFIX = os.getenv("TOKEN_BLACKLIST_PREFIX")
REFRESH_TOKEN_PREFIX = os.getenv("REFRESH_TOKEN_PREFIX")

# 예외처리
# 트랜잭션 관리
class AuthService:

    def __init__(self, redis_repo: RedisRepository, member_service: MemberService):
        self.redis_repo = redis_repo
        self.member_service = member_service

# redis에 refresh_token 저장
# key - 콜론 체이닝(값들을 콜론(,)으로 엮는 방식)
    async def save_refresh_token(self, member_id: int, refresh_token) -> None:
        try:
            key = f"{REFRESH_TOKEN_PREFIX}{member_id}"
            ex = 60 * 60 * 24 * 30  # 30일
            await self.redis_repo.set(key, refresh_token, ex=ex)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="save_refresh_token 오류"
            )


    #  redis에 등록된 refresh_token 유효한지 검사
    async def validate_refresh_token(self, member_id: int, refresh_token: str) -> bool:
        key = f"{REFRESH_TOKEN_PREFIX}{member_id}"
        saved_token= await self.redis_repo.get(key)
        return refresh_token == saved_token


    #  redis에 등록된 refresh_token 삭제
    async def delete_refresh_token(self, member_id: int):
        key = f"{REFRESH_TOKEN_PREFIX}{member_id}"
        await self.redis_repo.delete(key)

    #  redis에 등록된 access_token 무효화(로그아웃시)
    async def save_blacklisted_token(self, access_token: str) -> None:
        try:
            key = f"{TOKEN_BLACKLIST_PREFIX}{access_token}"
            ex = 60 * 60 * 24

            await self.redis_repo.set(key, "blacklisted", ex=ex)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="save_blacklisted_token 오류"
            )

    #  redis에 블랙리스트로 등록되어있는지 확인
    async def is_blacklisted_token(self, access_token: str) -> bool:
        key = f"{TOKEN_BLACKLIST_PREFIX}{access_token}"
        # True -> 블랙리스트
        # False -> 사용 가능
        return await self.redis_repo.exists(key)


    #  로그인
    async def login(self, login_request_dto: LoginRequestDTO) -> JwtTokenDTO:
        # 회원 조회
        member_in_db = await self.member_service.get_member_by_email_provider(
            login_request_dto.member_email,
            login_request_dto.member_provider
        )

        # 비밀번호 검증
        if not verify_password(
            login_request_dto.member_password,
            member_in_db.member_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="verify_password 비밀번호 불일치"
            )

        # JWT 토큰 만들기
        #   - 유저의 정보 중 최소한의 정보만 claim에 담기
        member_id = member_in_db.id
        claims = MemberClaimDTO(
            id=member_in_db.id,
            member_email=member_in_db.member_email,
            member_provider=member_in_db.member_provider
        )

        #   - 유틸 함수 이용해서 토큰(refresh, access) 만들기
        access_token = generate_access_token(claims)
        refresh_token = generate_refresh_token(claims)

        # refresh를 redis에 저장
        await self.save_refresh_token(member_id, refresh_token)

        # 토큰 반환
        return JwtTokenDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )
        


    #  소셜로그인
    #  로그아웃
    #  refresh => access 재발급





    # 레포지토리 주입 팩토리 함수
def get_auth_service(
    redis_repo: RedisRepository = Depends(get_redis_repository), 
    member_service: MemberService = Depends(get_member_service)
):
    return AuthService(redis_repo, member_service)