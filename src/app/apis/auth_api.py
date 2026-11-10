import os
from dotenv import load_dotenv
from fastapi import APIRouter, Query, Depends, Response
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.member_schema import MemberClaimDTO
from app.enums.member_enum import MemberProvider
from app.schemas.auth_schema import JwtTokenDTO, LoginRequestDTO, SocialLoginRequestDTO
from app.services.auth_service import AuthService, get_auth_service
from app.dependencies.auth_dependency import get_current_member, get_tokens

# 소셜 로그인용 import
import httpx  # 추가 요청 처리
from fastapi.responses import RedirectResponse  # 페이지 전환
from urllib.parse import urlencode  # 요청 주소를 조합하기 위한 라이브러리

load_dotenv()

router = APIRouter()

@router.post(
    "/login",
    response_model=ApiResponseDTO,
    summary="로컬 로그인",
    responses={
        200: {
            "description": "로그인 성공"
        },
        400: {
            "description": "비밀번호 불일치 등 잘못된 요청",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "아이디 또는 비밀번호가 일치하지 않습니다."
                    }
                }
            }
        },
        404: {
            "description": "존재하지 않는 회원",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "회원이 존재하지 않습니다."
                    }
                }
            }
        }
    }
)
async def login(
    login_member: LoginRequestDTO,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    login_member.member_provider = MemberProvider.LOCAL.value
    tokens = await auth_service.login(login_member)

    access_token = tokens.access_token
    refresh_token = tokens.refresh_token

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 30
    )

    print("tokens", tokens)

    return ApiResponseDTO(
        success=True,
        message="로그인 성공",
    )





GOOGLE_AUTH_URL=os.getenv("GOOGLE_AUTH_URL")
GOOGLE_TOKEN_URL=os.getenv("GOOGLE_TOKEN_URL")
GOOGLE_USERINFO_URL=os.getenv("GOOGLE_USERINFO_URL")
GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI=os.getenv("GOOGLE_REDIRECT_URI")
FRONTEND_URL=os.getenv("FRONTEND_URL")



# 구글 로그인
# /auth/google
@router.get(
    "/google",
    summary="구글 로그인"
)
async def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }

    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)

# 구글 로그인 콜백
# /auth/google/callback
@router.get(
    "/google/callback",
    summary="구글 로그인 콜백"
)
async def google_login_callback(
    code: str,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )

        token_data = token_res.json()
        access_token = token_data.get("access_token")

        async with httpx.AsyncClient() as client:
            user_res = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )

        user = user_res.json()

        user_params = {
            "member_email": user.get("email"),
            "member_provider": MemberProvider.GOOGLE.value,
            "member_provider_id": user.get("sub")
        }

        social_member = SocialLoginRequestDTO.model_validate(user_params)
        tokens = await auth_service.social_login_or_none(social_member)

        url = f"{FRONTEND_URL}/join-additional?{urlencode(user_params)}"
        return RedirectResponse(url)

    access_token = tokens.access_token
    refresh_token = tokens.refresh_token

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 30
    )

    return RedirectResponse(url=FRONTEND_URL)

        # social_member = SocialLoginRequestDTO(
        #     member_email=user.get("email"),
        #     member_provider=MemberProvider.GOOGLE.value,
        #     member_provider_id=user.get("sub")
        # )

        # await auth_service.social_login(social_member)


































        # 로그아웃
@router.post(
    "/logout",
    summary="로그아웃",
    response_model=ApiResponseDTO,
)
async def logout(
    response: Response,
    member_claims: MemberClaimDTO = Depends(get_current_member),
    tokens: JwtTokenDTO = Depends(get_tokens),
    auth_service: AuthService = Depends(get_auth_service)
):
    await auth_service.logout(tokens.access_token, tokens.refresh_token)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return ApiResponseDTO(
        success=True,
        message="로그아웃 성공"
    )
    # 1. Token -> Decode 후 로그아웃에 전달
    # 2. 로그아웃 서비스 실행
    # 3. 화면 쿠키를 삭제
    # 4. 화면으로 ApiResponseDTO를 응답