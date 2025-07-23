import logging
from searchright_technical_assignment.db.conn import engine, Base, SessionLocal
from searchright_technical_assignment.model.company import Company # Company 모델 임포트
from searchright_technical_assignment.model.companynews import CompanyNews # CompanyNews 모델 임포트
from searchright_technical_assignment.db.insert_company_data import insert_company_data
from searchright_technical_assignment.db.insert_company_news_data import insert_company_news_data
import asyncio # asyncio 임포트
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
# 테이블 스키마 생성 함수
def create_all_tables():
    print("모든 테이블을 생성합니다...")
    try:
        Base.metadata.create_all(engine)
        print("모든 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        print(f"테이블 생성 중 오류 발생: {e}")
        print("PostgreSQL 데이터베이스가 실행 중이고 접근 가능한지 확인하십시오.")

async def main_async():
    # 1. 테이블 생성
    create_all_tables()
    
    # 2. 초기 데이터 삽입 (선택 사항, 필요 시 주석 해제 및 데이터 전달)
    insert_company_data() # await 추가
    insert_company_news_data()
    # db_session = SessionLocal()
    # news_inserter = CompanyNewsInserter(db_session)
    # await news_inserter.insert_data()

if __name__ == "__main__":
    asyncio.run(main_async()) # 비동기 메인 함수 실행