from datetime import datetime
# from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field

# if TYPE_CHECKING:
#     from models.user import UserPublic

class PostBase(SQLModel):
    title: str = Field(index=True)
    content: str | None
    date: datetime

    author: int | None = Field(default=None, foreign_key="user.id")
    image_path: str | None = Field(default=None)

class Post(PostBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class PostPublic(PostBase):
    id: int

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    content: str | None = None

# class PostPublicWithUser(PostPublic):
#     user: Optional["UserPublic"]
