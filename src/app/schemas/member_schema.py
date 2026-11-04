from pydantic import BaseModel
from datetime import datetime
from app.enums.member_enum import MemberProvider

# VO
class MemberVO(BaseModel):
    id: int
    member_email: str
    member_password: str | None = None
    member_neme: str | None = None
    member_age: int | None = None
    member_profile: str | None = "/members/default.jpg"
    member_provider_id: str | None = None
    member_provider: MemberProvider | None = None
    member_created_at: datetime | None = None

# 이 중 id, member_provider_id, member_provider, member_created_at는 사용자에게서 받는 정보가 아님.
# 때문에 사용자에게서 받을 정보(프론트와 주고받아야 하는 정보)만 담아놓은 게 DTO

# DTO
class MemberCreateDTO(BaseModel):
    member_email: str
    member_password: str | None = None
    member_name: str | None = None
    member_age: int | None = None
    member_profile: str | None = "/members/default.jpg"
    member_provider: MemberProvider | None = None

    # ORM -> Pydantic
    class Config:
        from_attribures = True

class SosialMemberCreateDTO(BaseModel):
    member_email: str
    member_name: str | None = None
    member_age: int | None = None
    member_profile: str | None = "/members/default.jpg"
    member_provider: MemberProvider | None = None

    # ORM -> Pydantic
    class Config:
        from_attribures = True

class MemberClaimDTO(BaseModel):
    id: int
    member_email: str
    member_provider: str

    class Config:
        from_attribures = True

# 화면으로 보내는 DTO는 Response라는 이름을 붙임
class MemberResponseDTO(BaseModel):
    id: int
    member_email: str
    member_name: str | None = None
    member_age: int | None = None
    member_profile: str | None = "/members/default.jpg"
    member_provider_id: str | None = None
    member_provider: MemberProvider | None = None
    member_created_at: datetime | None = None

    class Config:
        from_attributes = True

class MemberUpdateDTO(BaseModel):
    member_password: str | None = None
    member_name: str | None = None
    member_age: int | None = None
    member_profile: str | None = "/members/default.jpg"

    class Config:
        from_attributes = True