#!/usr/bin/env python
import os
import csv
import logging
from datetime import datetime

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# 데이터베이스 연결 정보
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": os.getenv("POSTGRES_USER", "searchright"),
    "password": os.getenv("POSTGRES_PASSWORD", "searchright"),
    "database": os.getenv("POSTGRES_DB", "searchright"),
}


def connect_to_db():
    """
    PostgreSQL 데이터베이스에 연결합니다.

    Returns:
        psycopg2.extensions.connection: 데이터베이스 연결 객체.

    Raises:
        psycopg2.Error: 데이터베이스 연결에 실패한 경우 발생합니다.
    """
    logger.info("데이터베이스 연결 시도...")
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.info(f"성공적으로 {DB_CONFIG['database']} 데이터베이스에 연결했습니다.")
        return conn
    except psycopg2.Error as e:
        logger.error(f"데이터베이스 연결 오류: {e}")
        raise


def create_company_news_table(conn):
    """
    `company_news` 테이블을 생성합니다. 테이블이 이미 존재하는 경우 생성을 건너뜁니다.

    Args:
        conn (psycopg2.extensions.connection): 데이터베이스 연결 객체.

    Raises:
        psycopg2.Error: 테이블 생성에 실패한 경우 발생합니다.
    """
    logger.info("company_news 테이블 생성 확인...")
    try:
        with conn.cursor() as cursor:
            # 테이블이 존재하는지 확인
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'company_news'
                );
            """
            )
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                logger.info(
                    "company_news 테이블이 존재하지 않습니다. 새로운 테이블을 생성합니다."
                )
                cursor.execute(
                    """
                    CREATE TABLE company_news (
                        id SERIAL PRIMARY KEY,
                        company_id INTEGER NOT NULL,
                        title VARCHAR(1000) NOT NULL,
                        original_link TEXT,
                        news_date DATE NOT NULL,
                        FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
                    );
                """
                )
                logger.info("company_news 테이블이 성공적으로 생성되었습니다.")
            else:
                logger.info(
                    "company_news 테이블이 이미 존재합니다. 테이블 생성을 건너뜁니다."
                )
    except psycopg2.Error as e:
        logger.error(f"테이블 생성 오류: {e}")
        raise


def load_news_data(file_path):
    """
    지정된 CSV 파일에서 뉴스 데이터를 로드합니다.

    Args:
        file_path (str): 뉴스 데이터 CSV 파일의 경로.

    Returns:
        list: 로드된 뉴스 데이터를 담은 딕셔너리 리스트.
    """
    logger.info(f"뉴스 데이터 CSV 파일 로드 시도: {file_path}")
    news_data = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # 날짜 변환
                    year = int(row["year"])
                    month = int(row["month"])
                    day = int(row["day"])
                    news_date = datetime(year, month, day).strftime("%Y-%m-%d")

                    news_data.append(
                        {
                            "company_name": row["name"],
                            "title": row["title"],
                            "original_link": row["original_link"],
                            "news_date": news_date,
                        }
                    )
                except (ValueError, KeyError) as e:
                    logger.error(f"데이터 행 처리 오류: {e}, 행: {row}")
                    continue

            logger.info(f"{len(news_data)}개의 뉴스 데이터를 로드했습니다.")
            return news_data
    except FileNotFoundError as e:
        logger.error(f"파일 로드 오류 ({file_path}): {e}")
        return []


def get_company_map(conn):
    """
    `company` 테이블에서 회사 이름과 ID를 매핑하는 딕셔너리를 생성합니다.

    Args:
        conn (psycopg2.extensions.connection): 데이터베이스 연결 객체.

    Returns:
        dict: 회사 이름을 키로, 회사 ID를 값으로 하는 딕셔너리.
    """
    logger.info("회사 매핑 로드 시도...")
    try:
        company_map = {}
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name FROM company")
            for company_id, company_name in cursor.fetchall():
                company_map[company_name] = company_id

        logger.info(f"{len(company_map)}개의 회사 매핑을 로드했습니다.")
        return company_map
    except psycopg2.Error as e:
        logger.error(f"회사 매핑 로드 오류: {e}")
        return {}


def insert_news_data(conn, news_data, company_map):
    """
    뉴스 데이터를 데이터베이스의 `company_news` 테이블에 삽입합니다.
    이미 존재하는 뉴스 또는 회사 정보가 없는 뉴스는 건너뜁니다.

    Args:
        conn (psycopg2.extensions.connection): 데이터베이스 연결 객체.
        news_data (list): 삽입할 뉴스 데이터를 담은 딕셔너리 리스트.
        company_map (dict): 회사 이름과 ID 매핑 딕셔너리.

    Returns:
        int: 성공적으로 삽입된 뉴스 데이터의 개수.
    """
    logger.info("뉴스 데이터 삽입 시작...")
    try:
        inserted_count = 0
        skipped_count = 0
        missing_company_count = 0

        with conn.cursor() as cursor:
            for news in news_data:
                company_name = news["company_name"]

                # 회사 ID 찾기
                if company_name not in company_map:
                    missing_company_count += 1
                    logger.warning(
                        f"회사 '{company_name}'가 데이터베이스에 존재하지 않습니다. 해당 뉴스를 건너뜁니다."
                    )
                    continue

                company_id = company_map[company_name]

                # 중복 확인
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM company_news 
                    WHERE company_id = %s AND title = %s AND news_date = %s
                    """,
                    (company_id, news["title"], news["news_date"]),
                )
                count = cursor.fetchone()[0]

                if count > 0:
                    skipped_count += 1
                    logger.info(f"뉴스 '{news['title']}'가 이미 존재합니다. 건너뜁니다.")
                    continue

                # 데이터 삽입
                cursor.execute(
                    """
                    INSERT INTO company_news (company_id, title, original_link, news_date) 
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        company_id,
                        news["title"],
                        news["original_link"],
                        news["news_date"],
                    ),
                )
                inserted_count += 1

                # 로깅 (100개마다)
                if inserted_count % 100 == 0:
                    logger.info(f"{inserted_count}개의 뉴스 데이터가 삽입되었습니다.")

        logger.info(f"총 {inserted_count}개의 뉴스 데이터가 삽입되었습니다.")
        logger.info(f"중복으로 {skipped_count}개의 데이터가 건너뛰어졌습니다.")
        logger.info(
            f"존재하지 않는 회사로 인해 {missing_company_count}개의 데이터가 건너뛰어졌습니다."
        )

        return inserted_count
    except psycopg2.Error as e:
        logger.error(f"데이터 삽입 오류: {e}")
        conn.rollback()
        return 0


def main():
    """
    회사 뉴스 데이터 설정 스크립트의 메인 함수입니다.
    데이터베이스에 연결하고, `company_news` 테이블을 생성하며,
    CSV 파일에서 뉴스 데이터를 로드하여 데이터베이스에 삽입합니다.
    """
    logger.info("setup_company_news_data 스크립트 시작.")
    try:
        # 데이터베이스 연결
        conn = connect_to_db()

        # company_news 테이블 생성
        create_company_news_table(conn)

        # 회사 매핑 가져오기
        company_map = get_company_map(conn)
        if not company_map:
            logger.error("회사 정보를 가져오지 못했습니다. 프로세스를 중단합니다.")
            return

        # 뉴스 데이터 로드
        script_dir = os.path.dirname(os.path.abspath(__file__))
        news_csv_path = os.path.join(script_dir, "company_news.csv")
        news_data = load_news_data(news_csv_path)
        if not news_data:
            logger.error("뉴스 데이터를 로드하지 못했습니다. 프로세스를 중단합니다.")
            return

        # 데이터 삽입
        insert_news_data(conn, news_data, company_map)

    except Exception as e:
        logger.error(f"예상치 못한 오류가 발생했습니다: {e}")
    finally:
        if "conn" in locals() and conn:
            conn.close()
            logger.info("데이터베이스 연결이 닫혔습니다.")


if __name__ == "__main__":
    main()