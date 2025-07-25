import logging
from searchright_technical_assignment.db.conn import engine, Base, SessionLocal
from searchright_technical_assignment.model.company import Company # Company 모델 임포트
from searchright_technical_assignment.model.companynews import CompanyNews # CompanyNews 모델 임포트
from searchright_technical_assignment.db.insert_company_data import insert_company_data
from searchright_technical_assignment.db.insert_company_news_data import insert_company_news_data
from searchright_technical_assignment.db.insert_company_news_embeddings import run_insert_company_news_embeddings
import asyncio # asyncio 모듈 임포트
from sqlalchemy import text # text 임포트 추가

# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# SQLAlchemy 로거의 레벨을 경고로 설정하여 불필요한 로그를 줄입니다.
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)

def create_all_tables():
    """
    데이터베이스에 모든 테이블을 생성합니다.
    테이블이 이미 존재하는 경우 생성 작업을 건너뜁니다.
    """
    logger.info("모든 테이블을 생성합니다...")
    try:
        Base.metadata.create_all(engine)
        
        logger.info("모든 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        logger.error(f"테이블 생성 중 오류 발생: {e}")
        logger.error("PostgreSQL 데이터베이스가 실행 중이고 접근 가능한지 확인하십시오.")

async def main_async():
    """
    테이블 생성 및 초기 데이터 삽입을 위한 비동기 메인 함수입니다.
    """
    # 1. 테이블 생성
    create_all_tables()

    # 2. 초기 데이터 삽입 (선택 사항, 필요 시 주석 해제 및 데이터 전달)
    # insert_company_data()
    # await insert_company_news_data()
    db = SessionLocal()
    try:
        insert_company_data(db)
        await insert_company_news_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    # 스크립트가 직접 실행될 때 비동기 메인 함수를 실행합니다.
    asyncio.run(main_async())