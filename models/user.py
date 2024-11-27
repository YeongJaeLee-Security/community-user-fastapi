from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
#   from models.post import PostPublic
    from models.log import Log
    from models.report import Report

# class User(SQLModel, table=True):
#     id: int = Field(default=None, primary_key=True)
#     email: EmailStr
#     password: str
#     username: str
#     report_count: int = Field(default=0)

# class UserSignUp(SQLModel):
#     email: EmailStr
#     password: str
#     username: str

# class UserSignIn(SQLModel):
#     email: EmailStr
#     password: str

class UserSignBase(SQLModel):
    email: EmailStr
    password: str

class UserSignUp(UserSignBase):
    username: str

class UserSignIn(UserSignBase):
    pass

class UserBase(SQLModel):
    email: EmailStr = Field(index=True)
    password: str
    username: str
    report_count: int = Field(default=0)

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    reports: Optional[list["Report"]] = Relationship(back_populates="user")
    logs: Optional[list["Log"]] = Relationship(back_populates="user")

    # posts: list["Post"] = Relationship(back_populates="user")

class UserPublic(UserBase):
    id: int

class UserUpdate(UserBase):
    email: EmailStr | None = None
    password: str | None = None
    username: str | None = None
    report_count: int| None = None

# class UserPublicWithPosts(UserPublic):
#     posts: List["PostPublic"] = []
