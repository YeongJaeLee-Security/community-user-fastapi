from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, Depends, Query, File, UploadFile, Form
# from models.post import Post, PostPublic, PostCreate, PostUpdate
from models import Post, PostPublic, PostCreate, PostUpdate, PostPublicWithUser
from database.connection import SessionDep
from sqlmodel import select
from auth.authenticate import authenticate
from pathlib import Path
from datetime import datetime
import uuid

router = APIRouter()

UPLOAD_DIR = Path("uploaded_files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def save_file(file: UploadFile) -> Optional[str]:

    allowed_extensions = {".jpg", ".png"}
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only JPG and PNG files are allowed.")

    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = UPLOAD_DIR / unique_filename

    try:
        with file_path.open("wb") as f:
            f.write(await file.read())
        return str(file_path) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.post("/submit", response_model=PostPublic)
async def create_post(
    session: SessionDep,
    title: str = Form(...),
    content: str = Form(...),
    file: Optional[UploadFile] = None,
    user_id=Depends(authenticate)
):
    image_path = None

    if file:
        if file.filename:
            try:
                image_path = await save_file(file)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"File upload failed: {e}")
        else:
            image_path = None

    try:
        post = Post(
            title=title,
            content=content,
            author=user_id,
            date=datetime.utcnow(),
            image_path=image_path 
        )
        session.add(post)
        session.commit()
        session.refresh(post)
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/post", response_model=list[PostPublicWithUser])
def read_posts(session: SessionDep):
    posts = session.exec(select(Post)).all()
    return posts

@router.get("/post/{post_id}", response_model=PostPublicWithUser)
def read_post(*, post_id: int, session: SessionDep):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.patch("/post/{post_id}", response_model=PostPublic)
async def update_post(
    session: SessionDep,
    post_id: int,
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = None,
    remove_image: Optional[bool] = False,
):
    db_post = session.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 내용 업데이트
    if content is not None:
        db_post.content = content

    # 이미지 삭제
    if remove_image:
        db_post.image_path = None

    # 새로운 이미지 추가
    if file:
        allowed_extensions = {".jpg", ".png"}
        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid file format")

        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = UPLOAD_DIR / unique_filename

        with file_path.open("wb") as f:
            f.write(await file.read())

        db_post.image_path = str(file_path)

    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

@router.delete("/post/{post_id}/delete_image", response_model=PostPublic)
def delete_image(*, post_id: int, session: SessionDep):
    # 데이터베이스에서 게시물 가져오기
    db_post = session.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # image_path가 있는 경우 삭제
    if db_post.image_path:
        db_post.image_path = None  # 데이터베이스에서 이미지 경로 제거
        session.add(db_post)
        session.commit()
        session.refresh(db_post)
    else:
        raise HTTPException(status_code=400, detail="No image to delete")  # 삭제할 이미지가 없는 경우 예외 처리

    return db_post


@router.delete("/post/{post_id}")
def delete_post(*, post_id: int, session: SessionDep):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    session.delete(post)
    session.commit()
    return {"ok": True}

@router.get("/search/", response_model=list[PostPublicWithUser])
def search_post(
    *,
    title: Annotated[str | None, Query(max_length=50)] = None,
    session: SessionDep
):
    print(title)
    if title is None or title.strip() == "":
        raise HTTPException(status_code=400, detail="Search title cannot be empty")

    query = select(Post).where(Post.title.contains(title))
    posts = session.exec(query).all()
    return posts
