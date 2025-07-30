import os
import logging
from dotenv import load_dotenv
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# 데이터베이스 URL 가져오기
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    logger.error("환경 변수에 DATABASE_URL이 설정되어 있지 않습니다.")
    raise ValueError("환경 변수에서 DATABASE_URL을 찾을 수 없습니다.")
 
# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
# 세션 로컬 클래스 생성
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 선언적 기본 클래스 생성
Base = declarative_base()

# 의존성 주입을 위한 데이터베이스 세션
def get_db():
    db = SessionLocal()
    logger.info("데이터베이스 세션이 시작되었습니다.")
    try:
        yield db
    finally:
        db.close()
        logger.info("데이터베이스 세션이 닫혔습니다.")