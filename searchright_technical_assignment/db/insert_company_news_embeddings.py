import os
import logging
from datetime import datetime

import psycopg2
from sqlalchemy import create_engine, Column, Integer, String, Date, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import text

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from langchain.schema import Document

# 환경 변수 로드
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 데이터베이스 설정
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경 변수가 설정되지 않았습니다.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# PGVector 컬렉션 이름
COLLECTION_NAME = "company_news_vectors"

# OpenAI 임베딩
embeddings = OpenAIEmbeddings()

class CompanyNews(Base):
    __tablename__ = 'company_news'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer)
    title = Column(String)
    original_link = Column(Text)
    news_date = Column(Date)
    # content 컬럼이 있다면 추가 (현재 CSV에는 없으므로 주석 처리)
    # content = Column(Text)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_company_news_from_db():
    """데이터베이스에서 company_news 데이터를 가져옵니다."""
    db = SessionLocal()
    try:
        # content 컬럼이 없으므로 title만 사용
        news_items = db.query(CompanyNews.title, CompanyNews.news_date, CompanyNews.company_id).all()
        logger.info(f"데이터베이스에서 {len(news_items)}개의 뉴스 항목을 로드했습니다.")
        return news_items
    except Exception as e:
        logger.error(f"뉴스 데이터를 데이터베이스에서 가져오는 중 오류 발생: {e}")
        return []
    finally:
        db.close()

def insert_embeddings_to_pgvector(news_items):
    """뉴스 데이터를 임베딩하여 PGVector에 저장합니다."""
    documents = []
    for news in news_items:
        # PGVector에 저장할 Document 객체 생성
        # content 컬럼이 없으므로 title을 content로 사용
        # 실제 뉴스 내용(content)이 있다면 해당 컬럼을 사용해야 합니다.
        doc_content = news.title
        
        # 메타데이터에 news_date의 년, 월, 일 정보 추가
        news_date = news.news_date
        metadata = {
            "company_id": news.company_id,
            "title": news.title,
            "news_date": news_date.isoformat(), # ISO 형식 문자열로 저장
            "year": news_date.year,
            "month": news_date.month,
            "day": news_date.day
        }
        documents.append(Document(page_content=doc_content, metadata=metadata))

    if not documents:
        logger.info("임베딩할 문서가 없습니다.")
        return

    logger.info(f"{len(documents)}개의 문서를 PGVector에 삽입합니다. 컬렉션: {COLLECTION_NAME}")
    try:
        PGVector.from_documents(
            documents=documents,
            embedding=embeddings,
            collection_name=COLLECTION_NAME,
            connection_string=DATABASE_URL,
            pre_delete_collection=True # 기존 컬렉션이 있다면 삭제 후 새로 생성
        )
        logger.info("PGVector에 임베딩 삽입 완료.")
    except Exception as e:
        logger.error(f"PGVector에 임베딩 삽입 중 오류 발생: {e}")


if __name__ == "__main__":
    logger.info("PGVector 임베딩 삽입 스크립트 시작.")
    # PGVector 테이블이 없으면 자동으로 생성됩니다.
    # Base.metadata.create_all(engine) # PGVector는 자체적으로 테이블을 관리하므로 필요 없음

    news_data = get_company_news_from_db()
    if news_data:
        insert_embeddings_to_pgvector(news_data)
    else:
        logger.warning("PGVector에 삽입할 뉴스 데이터가 없습니다. company_news 테이블을 확인하세요.")
    logger.info("PGVector 임베딩 삽입 스크립트 종료.")
