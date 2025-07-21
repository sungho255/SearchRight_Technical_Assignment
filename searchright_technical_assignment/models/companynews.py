# company.py
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.dialects.postgresql import JSON 
from ..db.conn import Base

class CompanyNews(Base):
    __tablename__ = 'company_news'

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    original_link = Column(JSON)
    news_date = Column(Date)

    def __repr__(self):
        return f"<Company_News(id={self.id}, company_id='{self.company_id}', title='{self.title}', original_link='{self.original_link}', news_date='{self.news_date}')>"
