from time import time
from fastapi import HTTPException, status
from jose import jwt
from config.Settings import Settings

settings = Settings()

# JWT 토큰 생성 acess, refresh
def create_jwt_token(email: str, user_id: int) -> dict:
    access_payload = {"user": email, "user_id": user_id, "iat": time(), "exp": time() + 900}  # 15분 유효
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm="HS256")

    refresh_payload = {"user": email, "user_id": user_id, "iat": time(), "exp": time() + 604800}  # 7일 유효
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm="HS256")

    return {"access_token": access_token, "refresh_token": refresh_token}

# JWT 토큰 검증
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
        if time() > exp:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token expired")
        return payload
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

# JWT 토큰 갱신
def refresh_access_token(token: str):
    try:
        # 리프레시 토큰 검증
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
        if time() > exp:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Refresh token expired")
        ctime = time()
        print(ctime)
        print('내부검증완료')
        print(payload)

        # 새로운 액세스 토큰 발급
        email = payload["user"]
        user_id = payload["user_id"]
        new_access_token = create_jwt_token(email, user_id)["access_token"]


        print('새로발급된 accesstoken')
        print(new_access_token)

        return {"access_token": new_access_token}
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")