import logging
from sqlalchemy import Column, Integer, String, Date, Text, Index
from sqlalchemy.dialects.postgresql import JSONB 
from pgvector.sqlalchemy import Vector # pgvector 임포트
from searchright_technical_assignment.db.conn import Base

# 로깅 설정
logger = logging.getLogger(__name__)

class CompanyNews(Base):
    """
    회사 뉴스 정보를 저장하는 데이터베이스 모델입니다.
    """
    __tablename__ = 'company_news'
    __table_args__ = ({'schema': 'company_news_collection', 'extend_existing': True})  # 스키마 지정

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    chunk_index = Column(Integer, nullable=False, default=0)
    combined_embedding = Column(Vector(1536), nullable=True) # 1536차원 Vector 타입으로 변경
    original_link = Column(JSONB)
    news_date = Column(Date)

    __table_args__ = (
        Index('idx_combined_embedding_hnsw', combined_embedding, postgresql_using='hnsw', postgresql_ops={'combined_embedding': 'vector_cosine_ops'}),
        Index('idx_company_news_unique', 'company_id', 'title', 'news_date', 'chunk_index', unique=True)
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.debug(f"CompanyNews 인스턴스 생성됨: {self.title}")

    # def __repr__(self):
    #     return f"<Company_News(id={self.id}, company_id='{self.company_id}', title='{self.title}', original_link='{self.original_link}', news_date='{self.news_date}')>"