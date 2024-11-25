from fastapi import APIRouter, Depends
from auth.authenticate import authenticate  # authenticate 함수 가져오기

router = APIRouter()

@router.get("/loginstate")
async def check_login_status(user_id: int = Depends(authenticate)):
    return {"status": "logged_in", "user_id": user_id}
