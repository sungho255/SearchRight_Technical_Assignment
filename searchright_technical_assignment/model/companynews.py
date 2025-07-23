from sqlalchemy import Column, Integer, String, Date, Text, Index
from sqlalchemy.dialects.postgresql import JSON 
from pgvector.sqlalchemy import Vector # pgvector 임포트
from db.conn import Base

class CompanyNews(Base):
    __tablename__ = 'company_news'

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    chunk_index = Column(Integer, nullable=False, default=0)
    combined_embedding = Column(Vector(1536), nullable=True) # 1536차원 Vector 타입으로 변경
    original_link = Column(JSON)
    news_date = Column(Date)

    __table_args__ = (
        Index('idx_combined_embedding_hnsw', combined_embedding, postgresql_using='hnsw', postgresql_ops={'combined_embedding': 'vector_l2_ops'}),
        Index('idx_company_news_unique', 'company_id', 'title', 'news_date', 'chunk_index', unique=True)
    )

    # def __repr__(self):
    #     return f"<Company_News(id={self.id}, company_id='{self.company_id}', title='{self.title}', original_link='{self.original_link}', news_date='{self.news_date}')>"
