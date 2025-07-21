from sqlalchemy import create_engine
from searchright_technical_assignment.db.conn import Base, DATABASE_URL
from searchright_technical_assignment.models.company import Company # Company 모델 임포트
from searchright_technical_assignment.models.companynews import CompanyNews # CompanyNews 모델 임포트

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)

def drop_all_tables():
    print(f"데이터베이스 {DATABASE_URL}의 모든 테이블을 삭제합니다...")
    # Base.metadata에 모든 테이블 정보가 로드되도록 모델을 임포트한 후 drop_all 호출
    Base.metadata.drop_all(engine)
    print("모든 테이블이 성공적으로 삭제되었습니다.")

if __name__ == "__main__":
    drop_all_tables()