# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from auth.jwt_handler import verify_jwt_token


# # 요청이 들어올 때, Authorization 헤더에 토큰을 추출
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/signin")

# async def authenticate(token: str = Depends(oauth2_scheme)):
#     if not token:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="액세스 토큰이 누락되었습니다.")
    
#     payload = verify_jwt_token(token)
#     return payload["user_id"]

from fastapi import Depends, HTTPException, status, Request
from auth.jwt_handler import verify_jwt_token

async def authenticate(request: Request):
    # 쿠키에서 access_token 가져오기
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="액세스 토큰이 누락되었습니다.")
    
    try:
        # JWT 토큰 검증
        payload = verify_jwt_token(token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 액세스 토큰입니다.")
    
    return payload["user_id"]  # 검증된 사용자 ID 반환
