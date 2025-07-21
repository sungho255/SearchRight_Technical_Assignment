from searchright_technical_assignment.db.conn import engine, Base
from searchright_technical_assignment.models.company import Company # Company 모델 임포트
from searchright_technical_assignment.models.companynews import CompanyNews # CompanyNews 모델 임포트
from insert_company_data import insert_company_data
from insert_company_news_data import insert_company_news_data
import asyncio # asyncio 임포트

# 테이블 스키마 생성 함수
def create_all_tables():
    print("Creating all tables...")
    try:
        Base.metadata.create_all(engine)
        print("All tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        print("Please ensure your PostgreSQL database is running and accessible.")

async def main_async():
    # 1. 테이블 생성
    create_all_tables()
    
    # 2. 초기 데이터 삽입 (선택 사항, 필요 시 주석 해제 및 데이터 전달)
    insert_company_data() # await 추가
    await insert_company_news_data() # await 추가

if __name__ == "__main__":
    asyncio.run(main_async()) # 비동기 메인 함수 실행