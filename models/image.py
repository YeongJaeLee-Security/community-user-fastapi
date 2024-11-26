from sqlmodel import SQLModel, Field

class Image(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str  # 원본 파일 이름
    path: str  # 저장된 파일 경로
