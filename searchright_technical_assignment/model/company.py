import logging
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB 
from searchright_technical_assignment.db.conn import Base

# 로깅 설정
logger = logging.getLogger(__name__)

class Company(Base):
    """
    회사 정보를 저장하는 데이터베이스 모델입니다.
    """
    __tablename__ = 'company'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    data = Column(JSONB)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.debug(f"회사 인스턴스 생성됨: {self.name}")

    # def __repr__(self):
    #     return f"<Company(id={self.id}, name='{self.name}', industry='{self.industry}', location='{self.location}')>"