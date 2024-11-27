from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models.user import User

class Log(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    login_date: datetime
    user_agent: str
    user_id: int = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="logs")

class LogData(SQLModel):
    login_date: datetime
    user_agent: str
    user_id: int