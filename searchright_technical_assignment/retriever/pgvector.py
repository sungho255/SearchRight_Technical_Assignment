import os
import openai
import logging
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

# OpenAI API 키 설정 및 임베딩 모델 초기화
openai.api_key = os.getenv('OPENAI_API_KEY')
embeddings = OpenAIEmbeddings()

def retriever():
    """
    PGVector 기반의 문서 검색기(retriever)를 초기화하고 반환합니다.

    Returns:
        retriever: PGVector 검색기 인스턴스.
    """
    logger.info("PGVector 검색기 초기화 중.")
    # PGVector에 연결
    vectorstore = PGVector(
        connection_string=os.getenv('DATABASE_URL'),
        embedding_function=embeddings,
        collection_name="documents",
    )

    # 검색기 구성 (유사도 검색, 상위 5개 문서 반환)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    logger.info("PGVector 검색기 초기화 성공.")
    return retriever

def search_by_keyword(keyword: str, k: int = 5, start_date_obj: dict = None, end_date_obj: dict = None):
    """
    키워드를 사용하여 PGVector에서 코사인 유사도 검색을 수행하고,
    주어진 기간 내의 문서만 필터링하여 반환합니다.

    Args:
        keyword (str): 검색할 키워드.
        k (int): 반환할 문서의 최대 개수. 기본값은 5.
        start_date_obj (dict): 검색 시작 날짜 (예: {'year': 2023, 'month': 1}).
        end_date_obj (dict): 검색 종료 날짜 (예: {'year': 2023, 'month': 12}).

    Returns:
        list[Document]: 필터링된 관련 문서 리스트.
    """
    logger.info(f"키워드 '{keyword}'로 검색 시작, 반환 개수 k={k}")
    # PGVector에 연결
    vectorstore = PGVector(
        connection_string=os.getenv('DATABASE_URL'),
        embedding_function=embeddings,
        collection_name="company_news_vectors",
    )

    # 초기 검색은 더 많은 문서를 가져와서 나중에 필터링할 수 있도록 합니다.
    # k 값을 3배로 늘려 충분한 문서를 가져오도록 합니다.
    initial_k = k * 3 

    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": initial_k})
    logger.info(f"초기 검색을 위해 키워드 '{keyword}'로 {initial_k}개 문서 검색 중.")
    docs = retriever.get_relevant_documents(keyword)
    logger.info(f"키워드 '{keyword}'에 대해 초기 {len(docs)}개 문서 발견.")
    for i, doc in enumerate(docs):
        logger.debug(f"  문서 {i+1} (초기): 내용='{doc.page_content[:100]}...', 메타데이터={doc.metadata}")

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
            # 해당 월의 마지막 날짜를 정확히 계산
            last_day_of_month = calendar.monthrange(end_year, end_month)[1]
            end_date = datetime(end_year, end_month, last_day_of_month)
        
        logger.info(f"날짜로 필터링: 시작일={start_date}, 종료일={end_date}")

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
                    logger.debug(f"  날짜로 필터링된 문서: 문서 날짜={doc_date}, 메타데이터={doc.metadata}")
            else:
                # 날짜 메타데이터가 없는 문서는 필터링하지 않고 포함 (또는 제외, 정책에 따라)
                logger.debug(f"  날짜 메타데이터가 없어 포함된 문서: 메타데이터={doc.metadata}")
                filtered_docs.append(doc)
    else:
        # 날짜 필터가 없으면 모든 문서 포함
        logger.info("날짜 필터가 적용되지 않았습니다. 모든 초기 문서가 포함됩니다.")
        filtered_docs = docs
    
    logger.info(f"키워드 '{keyword}'에 대해 필터링된 문서: {len(filtered_docs)}개 문서.")
    for i, doc in enumerate(filtered_docs):
        logger.debug(f"  문서 {i+1} (필터링됨): 내용='{doc.page_content[:100]}...', 메타데이터={doc.metadata}")

    # 최종적으로 k개만 반환
    return filtered_docs[:k]