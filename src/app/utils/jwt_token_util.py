import os
from dotenv import load_dotenv
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from app.schemas.member_schema import MemberClaimDTO

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# 1. access_token 생성 함수
def generate_access_token(member_claim: MemberClaimDTO) -> str:
    # dto -> dict
    claims = member_claim.model_dump()
    # access_token 평균적인 사용 시간: 1분 ~ 5분
    expire = datetime.now(timezone.utc) + timedelta(days=1) # 일단 하루종일 사용하는 걸로 만들고 나중에 바꿀거임
    access_token = jwt.encode(
        {
            **claims,
            "exp": expire
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return access_token

# 2. refresh_token 생성 함수
def generate_refresh_token(member_claim: MemberClaimDTO) -> str:
    # dto -> dict
    claims = member_claim.model_dump()
    # access_token 평균적인 사용 시간: 1분 ~ 5분
    expire = datetime.now(timezone.utc) + timedelta(days=30) # 일단 하루종일 사용하는 걸로 만들고 나중에 바꿀거임
    access_token = jwt.encode(
        {
            **claims,
            "exp": expire
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return access_token

# 3. token_parsing 함수 (token -> user info)
def parse_token(token: str) -> MemberClaimDTO:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    member_id = payload["id"]
    member_email = payload["member_email"]
    member_provider = payload["member_provider"]

    # MemberClaimDTO.model_validate()
    
    return MemberClaimDTO(
        id=member_id,
        member_email=member_email,
        member_provider=member_provider
    )

# 4. refresh_token 이용해서 access_token 재발급
def reissue_access_token(refresh_token: str) -> str:
    claims = parse_token(refresh_token)
    new_acess_token = generate_access_token(claims)
    return new_acess_token

