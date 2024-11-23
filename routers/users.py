from fastapi import APIRouter, HTTPException, status, Depends
from models.users import User, UserSignIn, UserSignUp
from database.connection import get_session
from sqlmodel import select
from auth.hash_password import HashPassword

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
async def sign_in(data: UserSignIn, session=Depends(get_session)) -> dict:
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

    return {"message": "로그인에 성공했습니다."}
