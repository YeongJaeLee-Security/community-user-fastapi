from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from typing import Optional

class Image(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str  # 원본 파일 이름
    path: str  # 저장된 파일 경로

class Log(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    login_date: datetime
    user_agent: str
    user_referer: str
    user_id: int = Field(default=None, foreign_key="user.id")

    user: "User" = Relationship(back_populates="logs")

class LogData(SQLModel):
    login_date: datetime
    user_agent: str
    user_referer: str
    user_id: int

class Report(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    report_content: str
    report_date: datetime
    reporter_user_id: int
    user_id: int = Field(default=None, foreign_key="user.id")

    user: "User" = Relationship(back_populates="reports")

class ReportContent(SQLModel):
    user_id: int
    report_content: str

class PostBase(SQLModel):
    title: str = Field(index=True)
    content: str | None
    date: datetime

    author: int | None = Field(default=None, foreign_key="user.id")
    image_path: str | None = Field(default=None)

class Post(PostBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user: "User" = Relationship(back_populates="posts")

class PostPublic(PostBase):
    id: int

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    content: str | None = None
    image_path: Optional[str] = None

class UserSignBase(SQLModel):
    email: EmailStr
    password: str

class UserSignUp(UserSignBase):
    username: str

class UserSignIn(UserSignBase):
    pass

class UserBase(SQLModel):
    email: EmailStr = Field(index=True, unique=True)
    password: str
    username: str = Field(index=True, unique=True)
    report_count: int = Field(default=0)
    isBan: bool = Field(default=False)

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    reports: list[Report] = Relationship(back_populates="user")
    logs: list[Log] = Relationship(back_populates="user")
    posts: list[Post] = Relationship(back_populates="user")

class UserPublic(UserBase):
    id: int

class UserUpdate(UserBase):
    email: EmailStr | None = None
    password: str | None = None
    username: str | None = None
    report_count: int| None = None
    isBan: bool = Field(default=False)

class UserPublicWithPosts(UserPublic):
    posts: list[PostPublic] | None = []

class PostPublicWithUser(PostPublic):
    user: UserPublic

class BanUserRequest(SQLModel):
    user_id: int
    isBan: bool