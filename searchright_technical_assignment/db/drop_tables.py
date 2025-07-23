import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from searchright_technical_assignment.db.conn import Base
from searchright_technical_assignment.model.company import Company # Company 모델 임포트
from searchright_technical_assignment.model.companynews import CompanyNews # CompanyNews 모델 임포트

load_dotenv()

# 데이터베이스 엔진 생성
engine = create_engine(os.getenv('DATABASE_URL'))

def drop_all_tables():
    print(f"데이터베이스의 모든 테이블을 삭제합니다...")
    # Base.metadata에 모든 테이블 정보가 로드되도록 모델을 임포트한 후 drop_all 호출
    Base.metadata.drop_all(engine)
    print("모든 테이블이 성공적으로 삭제되었습니다.")

if __name__ == "__main__":
    drop_all_tables()