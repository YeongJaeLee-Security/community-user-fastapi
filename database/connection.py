from config.Settings import Settings
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

settings = Settings()

# 기본 URL에서 데이터베이스 이름 제거
BASE_DATABASE_URL = settings.DATABASE_URL

# 데이터베이스 이름 추출
DATABASE_NAME = settings.DATABASE_NAME

# 기본 연결 엔진 (DB 이름 없이 접속)
base_engine = create_engine(BASE_DATABASE_URL, echo=True)

# 실제 데이터베이스 연결 엔진
engine_url = create_engine(f"{settings.DATABASE_URL}/{settings.DATABASE_NAME}", echo=True)

def create_database_if_not_exists():
    """
    데이터베이스가 없으면 생성하는 함수
    """
    try:
        with base_engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME};"))
            connection.commit()  # 트랜잭션 커밋
        print(f"Database '{DATABASE_NAME}' checked or created.")
    except OperationalError as e:
        print("Failed to connect to the database server:", e)
        raise

def connection():
    """
    데이터베이스 연결 및 테이블 생성
    """
    # 데이터베이스가 없으면 생성
    create_database_if_not_exists()

    # SQLModel을 상속받은 모든 클래스를 기반으로 데이터베이스에 테이블 생성
    SQLModel.metadata.create_all(engine_url)

def get_session():
    """
    데이터베이스 세션 생성기
    """
    # 데이터베이스와 상호작용(CRUD)를 관리하는 객체
    # with 구문으로 자원 해제 가능
    with Session(engine_url) as session:
        yield session
