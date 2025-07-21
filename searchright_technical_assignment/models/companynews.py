from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.dialects.postgresql import JSON 
from pgvector.sqlalchemy import Vector # pgvector 임포트
from ..db.conn import Base

class CompanyNews(Base):
    __tablename__ = 'company_news'

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    title_embedding = Column(Vector(1536), nullable=True) # 1536차원 Vector 타입으로 변경
    original_link = Column(JSON)
    news_date = Column(Date)

    def __repr__(self):
        return f"<Company_News(id={self.id}, company_id='{self.company_id}', title='{self.title}', original_link='{self.original_link}', news_date='{self.news_date}')>"
