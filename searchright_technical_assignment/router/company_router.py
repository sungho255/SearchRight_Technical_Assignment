import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from crud.company_dao import CompanyDAO
from schema.company import CompanySchema
from db.conn import get_db

# 로깅 설정
logger = logging.getLogger(__name__)

# APIRouter 인스턴스 생성
router = APIRouter()

@router.get("/companies/{company_id}", response_model=CompanySchema)
def get_company_by_id(company_id: int, db: Session = Depends(get_db)):
    """
    주어진 ID를 사용하여 회사 정보를 조회합니다.

    Args:
        company_id (int): 조회할 회사의 고유 ID.
        db (Session): 데이터베이스 세션 의존성 주입.

    Returns:
        CompanySchema: 조회된 회사 정보.

    Raises:
        HTTPException: 회사 ID를 찾을 수 없는 경우 404 에러 발생.
    """
    logger.info(f"ID가 {company_id}인 회사에 대한 요청을 받았습니다.")
    dao = CompanyDAO(db)
    company = dao.get_by_id(company_id)
    if company is None:
        logger.warning(f"ID가 {company_id}인 회사를 찾을 수 없습니다.")
        raise HTTPException(status_code=404, detail="Company not found")
    logger.info(f"ID가 {company_id}인 회사를 성공적으로 조회했습니다.")
    return company