import os
import logging
from dotenv import load_dotenv

from sqlalchemy import create_engine
from contextlib import asynccontextmanager
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# 데이터베이스 URL 가져오기
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    logger.error("환경 변수에 DATABASE_URL이 설정되어 있지 않습니다.")
    raise ValueError("환경 변수에서 DATABASE_URL을 찾을 수 없습니다.")
 
 
# class DatabaseManager:
#     def __init__(self, url: str):
#         # SQLAlchemy 엔진 생성
#          self.engine = create_engine(
#             url,
#             pool_size=20,           # 동시 연결 수
#             max_overflow=10,        # 추가 허용 연결 수
#             pool_timeout=30,        # 연결 대기 시간
#             pool_recycle=1000,      # 연결 재사용 시간
#             pool_pre_ping=True,
#             echo=False,
#          )
         
#     # 의존성 주입을 위한 데이터베이스 세션
#     @contextmanager
#     def get_db():
#         """
#         데이터베이스 세션을 제공하는 컨텍스트 관리자입니다.
#         세션은 사용 후 자동으로 닫힙니다.

#         Yields:
#             Session: SQLAlchemy 데이터베이스 세션.
#         """
#         # 세션 로컬 클래스 생성
#         db = SessionLocal(
#             bind = engine,
#             autoflush = False,
#             autocommit = False,
#         )
#         logger.info("데이터베이스 세션이 시작되었습니다.")
#         try:
#             yield db
#         finally:
#             db.close()
#             logger.info("데이터베이스 세션이 닫혔습니다.")

# db_manager = DatabaseManager(DATABASE_URL)
 
 
# SQLAlchemy 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
# 세션 로컬 클래스 생성
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_= AsyncSession)

# 선언적 기본 클래스 생성
Base = declarative_base()

# 의존성 주입을 위한 데이터베이스 세션
@asynccontextmanager
async def get_db():
    """
    데이터베이스 세션을 제공하는 컨텍스트 관리자입니다.
    세션은 사용 후 자동으로 닫힙니다.

    Yields:
        Session: SQLAlchemy 데이터베이스 세션.
    """
    db = SessionLocal()
    logger.info("데이터베이스 세션이 시작되었습니다.")
    try:
        yield db
    finally:
        await db.close()
        logger.info("데이터베이스 세션이 닫혔습니다.")