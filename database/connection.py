from typing import Annotated

from config.settings import Settings
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy_utils import create_database, database_exists
from fastapi import Depends

settings = Settings()

# 기본 URL에서 데이터베이스 이름 제거
BASE_DATABASE_URL = settings.DATABASE_URL

# 데이터베이스 이름 추출
DATABASE_NAME = settings.DATABASE_NAME

# 기본 연결 엔진 (DB 이름 없이 접속)
base_engine = create_engine(BASE_DATABASE_URL, echo=True)

# 실제 데이터베이스 연결 URL
engine_url = f"{BASE_DATABASE_URL}/{DATABASE_NAME}"
connect_args = {"check_same_thread": False}

# 실제 데이터베이스 연결 엔진
engine = create_engine(engine_url, connect_args=connect_args, echo=True)

def create_database_if_not_exists():
    if not database_exists(engine_url):  # URL 문자열 전달
        create_database(engine_url)     # URL 문자열 전달

def connection():
    """
    데이터베이스 연결 및 테이블 생성
    """
    # 데이터베이스가 없으면 생성
    create_database_if_not_exists()

    # SQLModel을 상속받은 모든 클래스를 기반으로 데이터베이스에 테이블 생성
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    데이터베이스 세션 생성기
    """
    # 데이터베이스와 상호작용(CRUD)를 관리하는 객체
    # with 구문으로 자원 해제 가능
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
