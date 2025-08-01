import pandas as pd
import numpy as np
import json
import os
from datetime import date
import asyncio
import traceback
import logging
from tqdm.asyncio import tqdm as async_tqdm
from tqdm import tqdm

from sqlalchemy.orm import Session
from sqlalchemy import exists
from ..db.conn import SessionLocal, get_db
from ..model.companynews import CompanyNews
from ..model.company import Company
from ..util.embedding import generate_embedding

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from langchain.schema import Document

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# httpx 로거의 레벨을 경고로 설정하여 HTTP 요청 로그를 억제합니다.
logging.getLogger('httpx').setLevel(logging.WARNING)

# 데이터베이스 설정
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경 변수가 설정되지 않았습니다.")

# PGVector 컬렉션 이름
COLLECTION_NAME = "company_news_vectors"

# OpenAI 임베딩 (PGVector 초기화에 필요)
embeddings = OpenAIEmbeddings()

async def insert_company_news_and_vectors(db: Session):
    """
    회사 뉴스 데이터를 CSV 파일에서 읽어 데이터베이스에 삽입하고,
    뉴스 내용에 대한 임베딩을 생성하여 Pgvector에 저장합니다.
    중복을 확인하여 건너뛰거나 새로운 회사 정보를 추가합니다.
    """
    try:
        logger.info("CSV 파일 읽기 시작...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, '..', '..', 'example_datas', 'company_news_with_content_chunked.csv')
        df = pd.read_csv(csv_path, encoding='utf-8')

        logger.info(f"CSV 파일 읽기 완료. 총 {len(df)}개 뉴스 항목.")

        logger.info("회사 정보 매핑 로드...")
        company_map = {c.name: c.id for c in db.query(Company).all()}

        logger.info(f"{len(company_map)}개의 회사 정보 로드 완료.")
        logger.info("임베딩 생성 시작...")

        # 모든 뉴스 제목을 수집하여 배치 임베딩을 준비합니다.
        combined_embed_contents = df['chunked_content'].tolist()

        # 비동기 임베딩 함수를 await 키워드로 호출합니다.
        all_combined_embeddings = await generate_embedding(combined_embed_contents)
        logger.info("임베딩 생성 완료.")

        # example_datas 디렉토리 경로 설정
        example_datas_dir = os.path.join(script_dir, '..', '..', 'example_datas')

        logger.info("데이터베이스 삽입 시작...")
        inserted_count = 0
        skipped_count = 0
        missing_company_count = 0

        # PGVector에 삽입할 데이터 준비
        pg_texts = []
        pg_embeddings = []
        pg_metadatas = []

        for index, row in tqdm(df.iterrows(), total=len(df), desc="데이터베이스 삽입 중"):
            company_name = row['name']

            company_id = company_map.get(company_name)

            # 데이터베이스에 회사가 없으면 JSON 파일에서 로드하여 추가
            if not company_id:
                company_data = {}
                found_json_file = None
                for fname in os.listdir(example_datas_dir):
                    if fname.endswith('.json') and company_name in fname:
                        found_json_file = os.path.join(example_datas_dir, fname)
                        break

                if found_json_file and os.path.exists(found_json_file):
                    with open(found_json_file, 'r', encoding='utf-8') as f:
                        company_data = json.load(f)
                else:
                    logger.warning(f"경고: 회사 '{company_name}'에 대한 JSON 파일을 찾을 수 없습니다. 이 회사에 대한 뉴스를 건너뜠습니다.")
                    missing_company_count += 1
                    continue # 회사 정보가 없으면 해당 뉴스 건너뛰기

                company = Company(name=company_name, data=company_data)
                db.add(company)
                db.flush() # ID를 얻기 위해 flush
                company_id = company.id
                company_map[company_name] = company_id # 새로 추가된 회사 맵에 반영

            # 미리 생성된 임베딩을 인덱스를 통해 가져옵니다.
            combined_embedding = all_combined_embeddings[index]

            # 임베딩이 비어있는지 확인 (generate_embedding에서 오류 시 빈 리스트 반환 가능성)
            if not combined_embedding or not isinstance(combined_embedding, list) or len(combined_embedding) == 0:
                logger.warning(f"경고: 제목 '{row['title']}'에 대한 임베딩이 비어 있거나 유효하지 않습니다. 이 뉴스 항목을 건너뜠습니다.")
                skipped_count += 1 # 임베딩 오류도 건너뛴 것으로 처리
                continue # 해당 뉴스 항목 건너뛰기

            # news_date를 date 객체로 변환
            news_date_obj = date(row['year'], row['month'], row['day'])

            # 중복 확인: company_id, title, news_date 기준으로 중복 확인
            news_exists = db.query(exists().where(
                CompanyNews.company_id == company_id,
                CompanyNews.title == row['title'],
                CompanyNews.news_date == news_date_obj
            )).scalar()

            if news_exists:
                skipped_count += 1
                continue # 중복이면 건너뛰기

            news_item = CompanyNews(
                company_id=company_id,
                title=row['title'],
                content=row['chunked_content'],
                chunk_index=row['chunk_index'],
                combined_embedding=combined_embedding,
                original_link=row['original_link'],
                news_date=news_date_obj
            )
            db.add(news_item)
            inserted_count += 1

            # PGVector에 삽입할 데이터 추가
            pg_texts.append(row['chunked_content'])
            pg_embeddings.append(combined_embedding)
            pg_metadatas.append({
                "company_id": company_id,
                "title": row['title'],
                "news_date": news_date_obj.isoformat(),
                "chunk_index": row['chunk_index'],
                "original_link": row['original_link']
            })

        db.commit()
        logger.info(f"데이터 삽입 완료! 총 삽입: {inserted_count}, 건너뜀 (중복/빈 임베딩): {skipped_count}, 누락된 회사: {missing_company_count}")

        # PGVector에 임베딩 삽입
        if pg_texts:
            logger.info(f"{len(pg_texts)}개의 문서를 PGVector에 삽입합니다. 컬렉션: {COLLECTION_NAME}")
            # 기존 컬렉션 삭제 후 새로 생성
            vector_store = PGVector(
                collection_name=COLLECTION_NAME,
                connection_string=DATABASE_URL,
                embedding_function=embeddings, # PGVector 초기화에 필요
                pre_delete_collection=True,
                async_mode=True,
            )
            vector_store.add_embeddings(texts=pg_texts, embeddings=pg_embeddings, metadatas=pg_metadatas)
            logger.info("PGVector에 임베딩 삽입 완료.")
        else:
            logger.info("PGVector에 삽입할 문서가 없습니다.")

    except Exception as e:
        db.rollback()
        logger.error(f"오류 발생: {e}")
        logger.error(traceback.format_exc()) # 상세한 traceback 출력
    finally:
        pass # db.close() 제거

if __name__ == "__main__":
    with SessionLocal() as db:
        asyncio.run(insert_company_news_and_vectors(db))
