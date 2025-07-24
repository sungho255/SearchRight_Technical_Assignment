#!/usr/bin/env python
import os
import json
import glob
import logging

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


def create_company_table(conn):
    """
    `company` 테이블을 생성합니다. 테이블이 이미 존재하는 경우 생성을 건너뜁니다.

    Args:
        conn (psycopg2.extensions.connection): 데이터베이스 연결 객체.

    Raises:
        psycopg2.Error: 테이블 생성에 실패한 경우 발생합니다.
    """
    logger.info("company 테이블 생성 확인...")
    try:
        with conn.cursor() as cursor:
            # 테이블이 존재하는지 확인
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'company'
                );
            """
            )
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                logger.info(
                    "company 테이블이 존재하지 않습니다. 새로운 테이블을 생성합니다."
                )
                cursor.execute(
                    """
                    CREATE TABLE company (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        data JSONB NOT NULL
                    );
                """
                )
                logger.info("company 테이블이 성공적으로 생성되었습니다.")
            else:
                logger.info(
                    "company 테이블이 이미 존재합니다. 테이블 생성을 건너뜁니다."
                )
    except psycopg2.Error as e:
        logger.error(f"테이블 생성 오류: {e}")
        raise


def load_company_data(file_path):
    """
    지정된 JSON 파일에서 회사 데이터를 로드합니다.
    파일 이름에서 회사 이름을 추출합니다.

    Args:
        file_path (str): 회사 데이터 JSON 파일의 경로.

    Returns:
        tuple: (회사 이름, 회사 데이터) 튜플. 파일 로드 또는 파싱 실패 시 (None, None)을 반환합니다.
    """
    logger.info(f"회사 데이터 파일 로드 시도: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            # 파일 이름에서 회사 이름 추출 (예: company_ex1_비바리퍼블리카.json -> 비바리퍼블리카)
            company_name = os.path.basename(file_path).split("_")[-1].split(".")[0]
            logger.info(f"회사 데이터 로드 성공: {company_name}")
            return company_name, data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"파일 로드 오류 ({file_path}): {e}")
        return None, None


def insert_company_data(conn, name, data):
    """
    회사 데이터를 데이터베이스의 `company` 테이블에 삽입합니다.
    이미 존재하는 회사는 삽입을 건너뜁니다.

    Args:
        conn (psycopg2.extensions.connection): 데이터베이스 연결 객체.
        name (str): 회사 이름.
        data (dict): 회사 데이터 (JSONB 형식).

    Returns:
        bool: 데이터 삽입 성공 여부 (True: 성공, False: 실패 또는 건너뜀).
    """
    logger.info(f"회사 데이터 삽입 시도: {name}")
    try:
        with conn.cursor() as cursor:
            # 이미 존재하는지 확인
            cursor.execute("SELECT COUNT(*) FROM company WHERE name = %s", (name,))
            count = cursor.fetchone()[0]

            if count > 0:
                logger.info(
                    f"회사 '{name}'의 데이터가 이미 존재합니다. 삽입을 건너뜁니다."
                )
                return False

            # 데이터 삽입
            cursor.execute(
                "INSERT INTO company (name, data) VALUES (%s, %s)",
                (name, json.dumps(data)),
            )
            logger.info(f"회사 '{name}'의 데이터가 성공적으로 삽입되었습니다.")
            return True
    except psycopg2.Error as e:
        logger.error(f"데이터 삽입 오류: {e}")
        conn.rollback()
        return False


def main():
    """
    회사 데이터 설정 스크립트의 메인 함수입니다.
    데이터베이스에 연결하고, `company` 테이블을 생성하며,
    JSON 파일에서 회사 데이터를 로드하여 데이터베이스에 삽입합니다.
    """
    logger.info("setup_company_data 스크립트 시작.")
    try:
        # 데이터베이스 연결
        conn = connect_to_db()

        # company 테이블 생성
        create_company_table(conn)

        # 스크립트 디렉토리 기준 파일 찾기
        script_dir = os.path.dirname(os.path.abspath(__file__))
        company_files = glob.glob(os.path.join(script_dir, "company_ex*.json"))
        logger.info(f"{len(company_files)}개의 회사 데이터 파일을 찾았습니다.")

        # 데이터 처리 및 삽입
        success_count = 0
        for file_path in sorted(company_files):
            company_name, company_data = load_company_data(file_path)
            if company_name and company_data:
                if insert_company_data(conn, company_name, company_data):
                    success_count += 1

        logger.info(f"총 {success_count}개의 회사 데이터가 성공적으로 삽입되었습니다.")

    except Exception as e:
        logger.error(f"예상치 못한 오류가 발생했습니다: {e}")
    finally:
        if "conn" in locals() and conn:
            conn.close()
            logger.info("데이터베이스 연결이 닫혔습니다.")


if __name__ == "__main__":
    main()