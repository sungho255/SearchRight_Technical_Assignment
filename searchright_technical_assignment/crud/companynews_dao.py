import logging
from sqlalchemy.orm import Session
from searchright_technical_assignment.model.companynews import CompanyNews

# 로깅 설정
logger = logging.getLogger(__name__)

class CompanyNewsDAO:
    """
    회사 뉴스 데이터에 대한 데이터 접근 객체 (DAO) 클래스입니다.
    데이터베이스 세션을 통해 회사 뉴스 데이터를 조회, 생성, 수정, 삭제합니다.
    """
    def __init__(self, db: Session):
        """
        CompanyNewsDAO의 생성자입니다.

        Args:
            db (Session): SQLAlchemy 데이터베이스 세션.
        """
        self.db = db

    def get_by_id(self, news_id: int):
        """
        주어진 ID로 회사 뉴스 정보를 조회합니다.

        Args:
            news_id (int): 조회할 회사 뉴스의 고유 ID.

        Returns:
            CompanyNews: 조회된 회사 뉴스 객체 또는 None.
        """
        logger.info(f"ID가 {news_id}인 회사 뉴스 정보를 가져오는 중입니다.")
        return self.db.query(CompanyNews).filter(CompanyNews.id == news_id).first()

    def get_all(self):
        """
        모든 회사 뉴스 정보를 조회합니다.

        Returns:
            list[CompanyNews]: 모든 회사 뉴스 객체의 리스트.
        """
        logger.info("모든 회사 뉴스 정보를 가져오는 중입니다.")
        return self.db.query(CompanyNews).all()

    def create(self, news_data: dict):
        """
        새로운 회사 뉴스 정보를 생성합니다.

        Args:
            news_data (dict): 생성할 회사 뉴스의 데이터를 담은 딕셔너리.

        Returns:
            CompanyNews: 생성된 회사 뉴스 객체.
        """
        logger.info(f"회사 뉴스 데이터를 생성하는 중입니다: {news_data}")
        news = CompanyNews(**news_data)
        self.db.add(news)
        self.db.commit()
        self.db.refresh(news)
        logger.info(f"ID가 {news.id}인 회사 뉴스를 성공적으로 생성했습니다.")
        return news

    def update(self, news_id: int, updates: dict):
        """
        주어진 ID의 회사 뉴스 정보를 업데이트합니다.

        Args:
            news_id (int): 업데이트할 회사 뉴스의 고유 ID.
            updates (dict): 업데이트할 필드와 값을 담은 딕셔너리.

        Returns:
            CompanyNews: 업데이트된 회사 뉴스 객체 또는 None (뉴스를 찾을 수 없는 경우).
        """
        logger.info(f"ID가 {news_id}인 회사 뉴스를 업데이트하는 중입니다. 업데이트 내용: {updates}")
        news = self.db.query(CompanyNews).filter(CompanyNews.id == news_id).first()
        if not news:
            logger.warning(f"업데이트할 ID가 {news_id}인 회사 뉴스를 찾을 수 없습니다.")
            return None
        for key, value in updates.items():
            if hasattr(news, key):
                setattr(news, key, value)
        self.db.commit()
        self.db.refresh(news)
        logger.info(f"ID가 {news_id}인 회사 뉴스를 성공적으로 업데이트했습니다.")
        return news

    def delete(self, news_id: int):
        """
        주어진 ID의 회사 뉴스 정보를 삭제합니다.

        Args:
            news_id (int): 삭제할 회사 뉴스의 고유 ID.

        Returns:
            bool: 삭제 성공 여부 (True: 성공, False: 실패).
        """
        logger.info(f"ID가 {news_id}인 회사 뉴스를 삭제하는 중입니다.")
        news = self.db.query(CompanyNews).filter(CompanyNews.id == news_id).first()
        if not news:
            logger.warning(f"삭제할 ID가 {news_id}인 회사 뉴스를 찾을 수 없습니다.")
            return False
        self.db.delete(news)
        self.db.commit()
        logger.info(f"ID가 {news_id}인 회사 뉴스를 성공적으로 삭제했습니다.")
        return True