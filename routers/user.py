from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from models.log import Log
from models.user import User, UserSignIn, UserSignUp, UserPublicWithPosts
from database.connection import SessionDep
from sqlmodel import select
from auth.hash_password import HashPassword
from auth.jwt_handler import create_jwt_token
from datetime import datetime

router = APIRouter()

hash_password = HashPassword()

# 사용자 등록
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_new_user(data: UserSignUp, session: SessionDep) -> dict:
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
@router.post("/signin")
async def sign_in(data: UserSignIn, response: Response, session: SessionDep, request: Request) -> dict:
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

    # HttpOnly 쿠키생성해서 클라이언트 브라우저에 저장
    # 개발환경에선 HTTPS를 적용하기 힘들기 때문에 sesecure=False로설정하고 개발
    # 실제 배포시엔 HTTPS를 적용하고 True로 변경
    # samesite는 같은 사이트에서만 쿠키가 전송되게 설정함
    response.set_cookie(key="access_token", value=tokens["access_token"], httponly=True, secure=False, samesite='strict')
    response.set_cookie(key="refresh_token", value=tokens["refresh_token"], httponly=True, secure=False, samesite='strict')

    # 토큰이 잘 발급되었나 확인
    print("Access Token Set:", tokens["access_token"])
    print("Refresh Token Set:", tokens["refresh_token"])

    # 로그 저장
    log_data = Log(
        login_date=datetime.now(),
        user_agent=request.headers.get('user-agent'),
        user_id=user.id
    )

    session.add(log_data)
    session.commit()
    session.refresh(log_data)

    return {"message": "로그인에 성공했습니다."}

# 로그아웃 처리
@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return {"message": "로그아웃에 성공했습니다."}

# 토큰 삭제 확인용 endpoint
# (localhost:8000/docs 에서만 확인 할것)
# (httponly 쿠키로 토큰을 저장했기 때문에 js의 document.cookie로는 조회가 불가능함)
@router.get("/check_cookies")
async def check_cookies(request: Request):
    cookies = request.cookies
    if "access_token" not in cookies and "refresh_token" not in cookies:
        return {"message": "쿠키가 삭제되었습니다."}
    return {"message": "쿠키가 여전히 존재합니다."}

@router.get("/profile/{user_id}", response_model=UserPublicWithPosts)
def read_user(*, user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Auhtor not found")
    return user
