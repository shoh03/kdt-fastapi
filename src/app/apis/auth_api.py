from fastapi import APIRouter, Query, Depends, Response
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.member_schema import MemberClaimDTO
from app.enums.member_enum import MemberProvider
from app.schemas.auth_schema import JwtTokenDTO, LoginRequestDTO, SocialLoginRequestDTO
from app.services.auth_service import AuthService, get_auth_service

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


