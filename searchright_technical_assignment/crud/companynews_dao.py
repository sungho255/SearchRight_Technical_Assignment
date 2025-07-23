from sqlalchemy.orm import Session
from model.companynews import CompanyNews

class CompanyNewsDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, news_id: int):
        return self.db.query(CompanyNews).filter(CompanyNews.id == news_id).first()

    def get_all(self):
        return self.db.query(CompanyNews).all()

    def create(self, news_data: dict):
        news = CompanyNews(**news_data)
        self.db.add(news)
        self.db.commit()
        self.db.refresh(news)
        return news

    def update(self, news_id: int, updates: dict):
        news = self.db.query(CompanyNews).filter(CompanyNews.id == news_id).first()
        if not news:
            return None
        for key, value in updates.items():
            if hasattr(news, key):
                setattr(news, key, value)
        self.db.commit()
        self.db.refresh(news)
        return news

    def delete(self, news_id: int):
        news = self.db.query(CompanyNews).filter(CompanyNews.id == news_id).first()
        if not news:
            return False
        self.db.delete(news)
        self.db.commit()
        return True

    
