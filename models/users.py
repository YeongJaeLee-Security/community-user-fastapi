from pydantic import BaseModel, EmailStr
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    password: str
    username: str
    report_count: int


class UserSignIn(BaseModel):
    email: str
    password: str
