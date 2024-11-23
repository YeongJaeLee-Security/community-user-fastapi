from fastapi import APIRouter, HTTPException, status
from models.users import User, UserSignIn

user_router = APIRouter()

# 사용자 정보를 저장하는 딕셔너리 => DB 연동 처리

users = {}


# 사용자 등록
@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
def sign_new_user(data: User) -> dict:
    if data.email in users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="동일한 사용자가 존재합니다."
        )

    users[data.email] = data
    return {"message": "정상적으로 등록되었습니다."}


# 로그인 처리
@user_router.post("/signin")
def sign_in(data: UserSignIn) -> dict:
    if data.email not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 사용자가 존재하지 않습니다.",
        )

    user = users[data.email]
    if user.password != data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치하지 않습니다.",
        )

    return {"message": "로그인에 성공했습니다."}
