import os
import openai
import logging
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import calendar # calendar 모듈 임포트

# LangChain 관련 모듈 임포트
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정 및 임베딩 모델 초기화 (모듈 레벨에서 한 번만 초기화)
openai.api_key = os.getenv('OPENAI_API_KEY')
embeddings = OpenAIEmbeddings()

# PGVector 인스턴스를 위한 싱글톤 변수
_vectorstore_instance = None

def get_vectorstore_instance():
    """
    PGVector 인스턴스를 싱글톤 패턴으로 반환합니다.
    """
    global _vectorstore_instance
    if _vectorstore_instance is None:
        logger.info("PGVector 인스턴스 초기화 중...")
        _vectorstore_instance = PGVector(
            connection_string=os.getenv('PGVECTOR_DATABASE_URL'),
            embedding_function=embeddings,
            collection_name="company_news_vectors",
        )
        logger.info("PGVector 인스턴스 초기화 완료.")
    return _vectorstore_instance

def retriever():
    """
    PGVector 기반의 문서 검색기(retriever)를 초기화하고 반환합니다.
    """
    logger.info("PGVector 검색기 초기화 중.")
    # 싱글톤 인스턴스를 사용하여 검색기 구성
    retriever = get_vectorstore_instance().as_retriever(search_type="similarity", search_kwargs={"k": 5})
    logger.info("PGVector 검색기 초기화 성공.")
    return retriever


def _blocking_search(keyword: str, k: int, start_date_obj: dict = None, end_date_obj: dict = None):
    """
    동기적으로 PGVector 검색을 수행하는 내부 함수입니다.
    """
    logger.info(f"[Blocking] 키워드 '{keyword}'로 검색 시작, 반환 개수 k={k}")
    
    initial_k = k * 3
    # 싱글톤 인스턴스를 사용하여 검색기 구성
    retriever = get_vectorstore_instance().as_retriever(search_type="similarity", search_kwargs={"k": initial_k})
    logger.info(f"[Blocking] 초기 검색을 위해 키워드 '{keyword}'로 {initial_k}개 문서 검색 중.")
    docs = retriever.get_relevant_documents(keyword)
    logger.info(f"[Blocking] 키워드 '{keyword}'에 대해 초기 {len(docs)}개 문서 발견.")

    filtered_docs = []
    if start_date_obj or end_date_obj:
        start_date = None
        if start_date_obj and 'year' in start_date_obj:
            start_year = start_date_obj['year']
            start_month = start_date_obj.get('month', 1)
            start_date = datetime(start_year, start_month, 1)

        end_date = None
        if end_date_obj and 'year' in end_date_obj:
            end_year = end_date_obj['year']
            end_month = end_date_obj.get('month', 12)
            last_day_of_month = calendar.monthrange(end_year, end_month)[1]
            end_date = datetime(end_year, end_month, last_day_of_month)
        
        logger.info(f"[Blocking] 날짜로 필터링: 시작일={start_date}, 종료일={end_date}")

        for doc in docs:
            doc_year = doc.metadata.get('year')
            doc_month = doc.metadata.get('month')
            doc_day = doc.metadata.get('day')

            if doc_year and doc_month and doc_day:
                doc_date = datetime(doc_year, doc_month, doc_day)
                
                is_within_range = True
                if start_date and doc_date < start_date:
                    is_within_range = False
                if end_date and doc_date > end_date:
                    is_within_range = False
                
                if is_within_range:
                    filtered_docs.append(doc)
    else:
        filtered_docs = docs
    
    logger.info(f"[Blocking] 키워드 '{keyword}'에 대해 필터링된 문서: {len(filtered_docs)}개 문서.")
    return filtered_docs[:k]

async def search_by_keyword(keyword: str, k: int = 5, start_date_obj: dict = None, end_date_obj: dict = None):
    """
    키워드를 사용하여 PGVector에서 코사인 유사도 검색을 수행하고,
    주어진 기간 내의 문서만 필터링하여 반환합니다. (비동기 래퍼)
    """
    return await asyncio.to_thread(
        _blocking_search, 
        keyword, 
        k, 
        start_date_obj=start_date_obj, 
        end_date_obj=end_date_obj
    )