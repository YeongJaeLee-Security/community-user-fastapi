from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from models.users import User, UserSignIn, UserSignUp
from database.connection import get_session
from sqlmodel import select
from auth.hash_password import HashPassword
from auth.jwt_handler import create_jwt_token

user_router = APIRouter()

hash_password = HashPassword()

# 사용자 등록
@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_new_user(data: UserSignUp, session=Depends(get_session)) -> dict:
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="동일한 사용자가 존재합니다."
        )

    new_user = User(
        email=data.email, 
        password=hash_password.hash_password(data.password),
        username=data.username
        )
    
    session.add(new_user)
    session.commit()
    return {"message": "정상적으로 등록되었습니다."}


# 로그인 처리
@user_router.post("/signin")
async def sign_in(data: UserSignIn, response: Response, session=Depends(get_session)) -> dict:
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if not user:  
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 사용자가 존재하지 않습니다.",
        )

    if hash_password.verify_password(data.password, user.password) == False:    
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치하지 않습니다.",
        )
    # 로그인 성공시 토큰 발급 
    tokens = create_jwt_token(user.email, user.id)

    response.set_cookie(key="access_token", value=tokens["access_token"], httponly=True, secure=True, samesite="Strict")
    response.set_cookie(key="refresh_token", value=tokens["refresh_token"], httponly=True, secure=True, samesite="Strict")

    # 토큰이 잘 발급되었나 확인
    print("Access Token Set:", tokens["access_token"])
    print("Refresh Token Set:", tokens["refresh_token"])

    return {"message": "로그인에 성공했습니다."}

# 로그아웃 처리
@user_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token", httponly=True, secure=True, samesite="Strict")
    response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="Strict")
    
    return {"message": "로그아웃에 성공했습니다."}

# 토큰 삭제 확인용 endpoint
# (localhost:8000/docs 에서만 확인 할것)
# (httponly 쿠키로 토큰을 저장했기 때문에 js의 document.cookie로는 조회가 불가능함)
@user_router.get("/check_cookies")
async def check_cookies(request: Request):
    cookies = request.cookies
    if "access_token" not in cookies and "refresh_token" not in cookies:
        return {"message": "쿠키가 삭제되었습니다."}
    return {"message": "쿠키가 여전히 존재합니다."}