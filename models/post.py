from datetime import datetime

from sqlmodel import SQLModel, Field

class PostBase(SQLModel):
    title: str = Field(index=True)
    content: str | None
    date: datetime

    author: int = Field(foreign_key="user.id")

class Post(PostBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class PostPublic(PostBase):
    id: int

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    title: str | None = None
    content: str | None = None
