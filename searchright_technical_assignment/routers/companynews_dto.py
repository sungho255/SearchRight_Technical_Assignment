from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..crud.companynews_dao import CompanyNewsDAO
from ..schemas.companynews import CompanyNewsSchema
from ..db.conn import get_db

router = APIRouter()

@router.get("/companynews/{news_id}", response_model=CompanyNewsSchema)
def get_company_news_by_id(news_id: int, db: Session = Depends(get_db)):
    dao = CompanyNewsDAO(db)
    news = dao.get_by_id(news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="Company news not found")
    return news