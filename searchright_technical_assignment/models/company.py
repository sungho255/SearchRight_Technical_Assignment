# company.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON 
from ..db.conn import Base

class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    data = Column(JSON)

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', industry='{self.industry}', location='{self.location}')>"
