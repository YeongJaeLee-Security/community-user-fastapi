from typing import Annotated

from fastapi import APIRouter, HTTPException
from sqlmodel import select
from models.post import PostBase, Post, PostPublic, PostCreate, PostUpdate
from database.connection_temp import SessionDep

router = APIRouter()

@router.get("/", response_model=list[PostPublic])
def read_posts(
    session: SessionDep,
):
    posts = session.exec(select(Post)).all()
    return posts

@router.get("/post/{post_id}", response_model=PostPublic)
def read_post(post_id: int, session: SessionDep):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.post("/post/{post_id}", response_model=PostPublic)
def create_post(post: PostCreate, session: SessionDep):
    db_post = Post.model_validate(post)
    session.add(post)
    session.commit()
    session.refresh(post)
    return db_post

@router.patch("/post/{post_id}", response_model=PostPublic)
def update_post(post_id: int, post: PostUpdate, session: SessionDep):
    db_post = session.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    post_data = post.model_dump(exclude_unset=True)
    db_post.sqlmodel_update(post_data)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

@router.delete("/post/{post_id}")
def delete_post(post_id: int, session: SessionDep):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    session.delete(post)
    session.commit()
    return {"ok": True}
