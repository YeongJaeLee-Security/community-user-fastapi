from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from pathlib import Path
from sqlalchemy.orm import Session  # SQLAlchemy Session 사용
from models.image import Image  # Image 모델 가져오기
from database.connection import get_session  # 세션 의존성 주입 함수 가져오기

# 라우터 객체 생성
router = APIRouter()

# 파일 저장 경로 설정
UPLOAD_DIR = Path("uploaded_files")  # 업로드된 파일을 저장할 디렉토리
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # 디렉토리가 없으면 생성


@router.post("/upload-image/")
async def upload_image(
    file: UploadFile = File(...), 
    session: Session = Depends(get_session)  # 세션 주입
):
    
    # 파일 확장자 확인
    allowed_extensions = {".jpg", ".png"}
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only JPG and PNG files are allowed.")

    # 유니크 파일 이름 생성 (중복 방지)
    unique_filename = f"{Path(file.filename).stem}_{Path(file.filename).suffix}"
    file_path = UPLOAD_DIR / unique_filename

    # 파일 저장
    try:
        with file_path.open("wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    # 데이터베이스에 파일 경로 저장
    image_record = Image(name=file.filename, path=str(file_path))
    session.add(image_record)
    session.commit()

    return {
        "filename": file.filename,
        "message": "File uploaded successfully",
        "path": str(file_path),
    }
