from fastapi import Depends, HTTPException, status, Request, Response
from auth.jwt_handler import verify_jwt_token, refresh_access_token

async def authenticate(request: Request, response: Response):

    #Access Token 확인
    access_token = request.cookies.get("access_token")
    if access_token:
        try:
        # JWT 토큰 검증
            payload = verify_jwt_token(access_token)
            return payload["user_id"]

        except Exception:
            pass

    # Refresh Token 확인
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰이 누락되었습니다.")

        # Refresh Token 검증 및 새로운 access token 발급
    try:
        # 새 엑세스 토큰 발급 (refresh_access_token 함수로 처리)
        new_access_token = refresh_access_token(refresh_token)


        # 새로운 액세스 토큰을 쿠키에 저장
        response.set_cookie(key="access_token", value=new_access_token["access_token"], httponly=True, secure=False, samesite='strict')

        # 인증 성공, user_id 반환
        payload = verify_jwt_token(new_access_token["access_token"])  # 새로 발급된 액세스 토큰을 검증
        return payload["user_id"]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="리프레시 토큰이 유효하지 않습니다."
        )