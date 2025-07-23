from sqlalchemy.orm import Session
from model.company import Company 

class CompanyDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, company_id: int):
        return self.db.query(Company).filter(Company.id == company_id).first()

    def get_all(self):
        return self.db.query(Company).all()

    def create(self, company_data: dict):
        company = Company(**company_data)
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def update(self, company_id: int, updates: dict):
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return None
        for key, value in updates.items():
            if hasattr(company, key):  # 안전하게 속성 체크
                setattr(company, key, value)
        self.db.commit()
        self.db.refresh(company)
        return company

    def delete(self, company_id: int):
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return False
        self.db.delete(company)
        self.db.commit()
        return True

    
