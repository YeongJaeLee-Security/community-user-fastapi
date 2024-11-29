from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
# from models.log import Log
# from models.user import User, UserSignIn, UserSignUp
from models import Log, LogData
from models import User, UserSignIn, UserSignUp
from models import UserPublic, UserUpdate, UserPublicWithPosts
from database.connection import SessionDep
from sqlmodel import select
from auth.hash_password import HashPassword
from auth.jwt_handler import create_jwt_token
from datetime import datetime

from auth.authenticate import authenticate

router = APIRouter()

hash_password = HashPassword()

# 사용자 등록
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_new_user(data: UserSignUp, session: SessionDep) -> dict:
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="동일한 사용자 이메일이 존재합니다."
        )

    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="동일한 사용자 이름이 존재합니다."
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
    # 개발환경에선 HTTPS를 적용하기 힘들기 때문에 secure=False로설정하고 개발
    # 실제 배포시엔 HTTPS를 적용하고 True로 변경
    # samesite는 같은 사이트에서만 쿠키가 전송되게 설정함
    response.set_cookie(key="access_token", value=tokens["access_token"], httponly=True, secure=False, samesite='strict')
    response.set_cookie(key="refresh_token", value=tokens["refresh_token"], httponly=True, secure=False, samesite='strict')

    # 토큰이 잘 발급되었나 확인
    # 배포 할땐 삭제예정
    print("Access Token Set:", tokens["access_token"])
    print("Refresh Token Set:", tokens["refresh_token"])

    # 로그 저장
    log_data = Log(
        login_date=datetime.now(),
        user_agent=request.headers.get('user-agent'),
        user_referer=request.headers.get("Referer"),
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

@router.get("/profile", response_model=list[UserPublicWithPosts])
def read_users(session: SessionDep):
    users = session.exec(select(User)).all()
    return users

@router.get("/profile/{user_id}", response_model=UserPublicWithPosts)
def read_user(*, user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/settings", response_model=UserPublicWithPosts)
def read_auth(
    *,
    auth_id: int = Depends(authenticate),
    session: SessionDep
):
    auth = session.get(User, auth_id)
    if not auth:
        raise HTTPException(status_code=404, detail="Auth not found")
    return auth

@router.patch("/settings", response_model=UserPublic)
def update_auth(
    *,
    auth_id: int = Depends(authenticate),
    auth: UserUpdate,
    session: SessionDep
):
    db_auth = session.get(User, auth_id)
    if not db_auth:
        raise HTTPException(status_code=404, detail="User not found")

    statement = select(User).where(User.email == auth.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="동일한 이메일이 존재합니다."
        )
    statement = select(User).where(User.username == auth.username)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="동일한 사용자 이름이 존재합니다."
        )

    auth_data = auth.model_dump(exclude_unset=True)
    db_auth.sqlmodel_update(auth_data)
    session.add(db_auth)
    session.commit()
    session.refresh(db_auth)

    return db_auth

@router.delete("/settings")
def delete_auth(
    *,
    auth_id: int = Depends(authenticate),
    session: SessionDep
):
    auth = session.get(User, auth_id)
    if not auth:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(auth)
    session.commit()
    return {"ok": True}

# 사용자 전체 조회 - 관리자만 사용
@router.get("/user", status_code=status.HTTP_200_OK)
def read_user_all(session: SessionDep):
    try:
        stmt = select(User.id, User.email, User.username, User.report_count)
        result = session.exec(stmt).all()

        users = [
            {
                "id": user[0],
                "email": user[1],
                "username": user[2],
                "report_count": user[3]
            }
            for user in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="INTERNAL_SERVER_ERROR"
        )

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found."
        )
    
    return { "message": users }

# 사용자 로그 전체 조회 - 관리자만 사용
@router.get("/user/log", status_code=status.HTTP_200_OK, response_model=list[LogData])
def read_user_log_all(session: SessionDep):
    try:
        logs = session.exec(select(Log)).all()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL_SEVER_ERROR")

    if not logs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자 로그 조회 실패")
    
    return logs

# 사용자별 로그 조회 - 관리자만 사용
@router.get("/user/log/{user_id}", status_code=status.HTTP_200_OK)
def read_user_log(user_id: int, session: SessionDep):
    try:
        log_by_user_id = session.exec(select(Log).where(Log.user_id==user_id)).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL_SEVER_ERROR")
    
    if not log_by_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자 로그 조회 실패")
    
    return log_by_user_id
