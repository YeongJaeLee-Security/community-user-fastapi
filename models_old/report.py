from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models.user import User

class Report(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    report_content: str
    report_date: datetime
    reporter_user_id: int
    user_id: int = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="reports")

class ReportContent(SQLModel):
    user_id: int
    report_content: str