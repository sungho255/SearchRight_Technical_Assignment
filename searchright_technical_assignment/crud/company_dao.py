import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from searchright_technical_assignment.model.company import Company

# 로깅 설정
logger = logging.getLogger(__name__)

class CompanyDAO:
    """
    회사 데이터에 대한 데이터 접근 객체 (DAO) 클래스입니다.
    데이터베이스 세션을 통해 회사 데이터를 조회, 생성, 수정, 삭제합니다.
    """
    def __init__(self, db: AsyncSession):
        """
        CompanyDAO의 생성자입니다.

        Args:
            db (AsyncSession): SQLAlchemy 비동기 데이터베이스 세션.
        """
        self.db = db

    async def get_by_id(self, company_id: int):
        """
        주어진 ID로 회사 정보를 조회합니다.

        Args:
            company_id (int): 조회할 회사의 고유 ID.

        Returns:
            Company: 조회된 회사 객체 또는 None.
        """
        logger.info(f"ID가 {company_id}인 회사 정보를 가져오는 중입니다.")
        result = await self.db.execute(select(Company).filter(Company.id == company_id))
        return result.scalars().first()

    async def get_all(self):
        """
        모든 회사 정보를 조회합니다.

        Returns:
            list[Company]: 모든 회사 객체의 리스트.
        """
        logger.info("모든 회사 정보를 가져오는 중입니다.")
        result = await self.db.execute(select(Company))
        return result.scalars().all()

    async def create(self, company_data: dict):
        """
        새로운 회사 정보를 생성합니다.

        Args:
            company_data (dict): 생성할 회사의 데이터를 담은 딕셔너리.

        Returns:
            Company: 생성된 회사 객체.
        """
        logger.info(f"회사 데이터를 생성하는 중입니다: {company_data}")
        company = Company(**company_data)
        self.db.add(company)
        await self.db.commit()
        await self.db.refresh(company)
        logger.info(f"ID가 {company.id}인 회사를 성공적으로 생성했습니다.")
        return company

    async def update(self, company_id: int, updates: dict):
        """
        주어진 ID의 회사 정보를 업데이트합니다.

        Args:
            company_id (int): 업데이트할 회사의 고유 ID.
            updates (dict): 업데이트할 필드와 값을 담은 딕셔너리.

        Returns:
            Company: 업데이트된 회사 객체 또는 None (회사를 찾을 수 없는 경우).
        """
        logger.info(f"ID가 {company_id}인 회사를 업데이트하는 중입니다. 업데이트 내용: {updates}")
        company = await self.get_by_id(company_id)
        if not company:
            logger.warning(f"업데이트할 ID가 {company_id}인 회사를 찾을 수 없습니다.")
            return None
        for key, value in updates.items():
            if hasattr(company, key):  # 속성 존재 여부 안전하게 확인
                setattr(company, key, value)
        await self.db.commit()
        await self.db.refresh(company)
        logger.info(f"ID가 {company.id}인 회사를 성공적으로 업데이트했습니다.")
        return company

    async def delete(self, company_id: int):
        """
        주어진 ID의 회사 정보를 삭제합니다.

        Args:
            company_id (int): 삭제할 회사의 고유 ID.

        Returns:
            bool: 삭제 성공 여부 (True: 성공, False: 실패).
        """
        logger.info(f"ID가 {company_id}인 회사를 삭제하는 중입니다.")
        company = await self.get_by_id(company_id)
        if not company:
            logger.warning(f"삭제할 ID가 {company_id}인 회사를 찾을 수 없습니다.")
            return False
        await self.db.delete(company)
        await self.db.commit()
        logger.info(f"ID가 {company.id}인 회사를 성공적으로 삭제했습니다.")
        return True

    async def get_data_by_names(self, companynames_and_dates: list):
        """
        회사 이름 리스트를 기반으로 회사 데이터(이름 및 데이터 필드)를 조회합니다.

        Args:
            companynames_and_dates (list): 회사 이름과 날짜 정보를 포함하는 딕셔너리 리스트.

        Returns:
            list: (회사 이름, 회사 데이터) 튜플의 리스트.
        """
        logger.info(f"이름으로 회사 데이터를 가져오는 중입니다: {companynames_and_dates}")
        company_names = [item['companyName'] for item in companynames_and_dates if 'companyName' in item]
        
        if not company_names:
            logger.info("회사 이름이 없어 데이터를 가져오지 않습니다.")
            return []

        result = await self.db.execute(
            select(Company.name, Company.data).filter(Company.name.in_(company_names))
        )
        matched_companies_results = result.all() 
        logger.info(f"일치하는 회사 {len(matched_companies_results)}개를 찾았습니다.")
            
        return matched_companies_results