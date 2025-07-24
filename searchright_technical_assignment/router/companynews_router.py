import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from searchright_technical_assignment.crud.companynews_dao import CompanyNewsDAO
from searchright_technical_assignment.schema.companynews import CompanyNewsSchema
from searchright_technical_assignment.db.conn import get_db

# 로깅 설정
logger = logging.getLogger(__name__)

# APIRouter 인스턴스 생성
router = APIRouter()

@router.get("/companynews/{news_id}", response_model=CompanyNewsSchema)
def get_company_news_by_id(news_id: int, db: Session = Depends(get_db)):
    """
    주어진 ID를 사용하여 회사 뉴스 정보를 조회합니다.

    Args:
        news_id (int): 조회할 회사 뉴스의 고유 ID.
        db (Session): 데이터베이스 세션 의존성 주입.

    Returns:
        CompanyNewsSchema: 조회된 회사 뉴스 정보.

    Raises:
        HTTPException: 뉴스 ID를 찾을 수 없는 경우 404 에러 발생.
    """
    logger.info(f"ID가 {news_id}인 회사 뉴스에 대한 요청을 받았습니다.")
    dao = CompanyNewsDAO(db)
    news = dao.get_by_id(news_id)
    if news is None:
        logger.warning(f"ID가 {news_id}인 회사 뉴스를 찾을 수 없습니다.")
        raise HTTPException(status_code=404, detail="Company news not found")
    logger.info(f"ID가 {news_id}인 회사 뉴스를 성공적으로 조회했습니다.")
    return news