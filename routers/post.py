from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile
# from models.post import Post, PostPublic, PostCreate, PostUpdate
from models import Post, PostPublic, PostCreate, PostUpdate, PostPublicWithUser
from database.connection import SessionDep
from sqlmodel import select
from auth.authenticate import authenticate
from pathlib import Path
import uuid

router = APIRouter()

UPLOAD_DIR = Path("uploaded_files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def save_file(file: UploadFile) -> str | None:
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
    *,
    post: PostCreate,
    user_id=Depends(authenticate),
    session: SessionDep,
):
    extra_data = {}

    if post.file:
        if post.file.filename:
            try:
                extra_data["image_path"] = await save_file(post.file)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

    try:
        post.author = user_id
        db_post = Post.model_validate(post, update=extra_data)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)
        return db_post
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
    *,
    post_id: int,
    post: PostUpdate,
    session: SessionDep,
):
    db_post = session.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    post_data = post.model_dump(exclude_unset=True)
    extra_data = {}
    if post_data["remove_image"]:
        extra_data["image_path"] = None

    if "file" in post_data:
        allowed_extensions = {".jpg", ".png"}
        file_extension = Path(post_data["file"]["file_name"]).suffix.lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid file format")

        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = UPLOAD_DIR / unique_filename

        with file_path.open("wb") as f:
            f.write(await file.read())
        extra_data["image_path"] = str(file_path)

    db_post.sqlmodel_update(post_data, update=extra_data)
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
    if title is None or title.strip() == "":
        raise HTTPException(status_code=400, detail="Search title cannot be empty")

    query = select(Post).where(Post.title.contains(title))
    posts = session.exec(query).all()
    return posts
