from fastapi import APIRouter, HTTPException, status, Body, Depends
from models import Report, ReportContent
from models import User
from auth.authenticate import authenticate
from database.connection import SessionDep
from datetime import datetime
from sqlmodel import select

router = APIRouter()

@router.post("/report", status_code=status.HTTP_201_CREATED)
def create_report(*, data: ReportContent=Body(..., description="신고 내용"),
                  user_id=Depends(authenticate), session: SessionDep):
    # data.user_id가 있는지 조회(신고할 대상이 있는지 조회)
    report_user = session.get(User, data.user_id)

    if not report_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일치하는 사용자가 없습니다.")

    # 그럴릴 없겠지만,, 본인 일 경우 return
    if data.user_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 접근입니다.")
    # report_count >= 10 이상인지 검사
    if report_user.report_count >= 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 접근입니다.")

    # 아니면, 신고 insert
    newReport = Report(report_content=data.report_content,
                       user_id=data.user_id, report_date=datetime.now(),
                       reporter_user_id=user_id)
    report_user.report_count += 1

    session.add(newReport)
    session.add(report_user)
    session.commit()
    session.refresh(newReport)
    session.add(report_user)

    return { "message" : "신고가 접수 되었습니다." }

# 신고 전체 조회
@router.get("/report", status_code=status.HTTP_200_OK)
def read_report_all(session: SessionDep):
    try:
        reports = session.exec(select(Report)).all()
    except Exception as e :
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL_SEVER_ERROR")

    if not reports:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="신고 내역이 없습니다.")
    
    return { "message" : reports }

# 사용자별 신고 조회
@router.get("/report/{user_id}", status_code=status.HTTP_200_OK)
def read_report(user_id: int, session: SessionDep):
    try:
        reports_by_user_id = session.exec(select(Report).where(Report.user_id==user_id)).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL_SEVER_ERROR")
    
    if not reports_by_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="신고 내역이 없습니다.")
    
    return  { "message" : reports_by_user_id }