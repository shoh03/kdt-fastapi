from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # 클릭 재킹 방지: 클릭 재킹은 버튼위에 투명한 다른 버튼을 만들어서 모방 사이트에 접속하게 만듦.
        response.headers["X-Frame-Options"] = "DENY"
        # MIME 스니핑 방지: MIME 스니핑은 주소 자리에 경로 형식이 아닌 코드를 넣어서 실행되도록 만듦.
        response.headers["X-Content-Type-Option"] = "nosniff"
        # XSS 방지(CSP): 사이트를 똑같이 만들고 바이러스를 심어놓음.
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' 'unsafe-inline' https:;"
        )
        return response

# 보안 미들웨어
def set_up_security(app: FastAPI):
    app.add_middleware(SecurityHeadersMiddleware)