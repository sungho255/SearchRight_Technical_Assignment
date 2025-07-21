from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..crud.company_dao import CompanyDAO
from ..schemas.company import CompanySchema
from ..db.conn import get_db

router = APIRouter()

@router.get("/companies/{company_id}", response_model=CompanySchema)
def get_company_by_id(company_id: int, db: Session = Depends(get_db)):
    dao = CompanyDAO(db)
    company = dao.get_by_id(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company