import pandas as pd
import numpy as np
import json
import os
from datetime import date
import asyncio # asyncio 모듈 임포트
import traceback # traceback 모듈 임포트

from sqlalchemy.orm import Session
from sqlalchemy import exists
from searchright_technical_assignment.db.conn import SessionLocal, get_db
from searchright_technical_assignment.models.companynews import CompanyNews
from searchright_technical_assignment.models.company import Company
from searchright_technical_assignment.utils.embedding import generate_embedding

async def insert_company_news_data(): # 함수를 비동기 함수로 변경
    db: Session = SessionLocal()
    try:
        print("1. CSV 파일 읽기 시작...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, '..', '..', 'example_datas', 'company_news.csv')
        df = pd.read_csv(csv_path)
        
        print(f"2. CSV 파일 읽기 완료. 총 {len(df)}개 뉴스 항목.")
        
        
        print("2.5. 회사 정보 매핑 로드...")
        company_map = {c.name: c.id for c in db.query(Company).all()}
        
        print(f"{len(company_map)}개의 회사 정보 로드 완료.")

        print("3. 임베딩 생성 시작...")
        # 모든 뉴스 제목을 수집하여 배치 임베딩을 준비합니다.
        titles_to_embed = df['title'].tolist()
        # 비동기 임베딩 함수를 await 키워드로 호출합니다.
        all_title_embeddings = await generate_embedding(titles_to_embed)
        print("임베딩 생성 완료.")

        # example_datas 디렉토리 경로 설정
        example_datas_dir = os.path.join(script_dir, '..', '..', 'example_datas')

        print("4. 데이터베이스 삽입 시작...")
        inserted_count = 0
        skipped_count = 0
        missing_company_count = 0

        for index, row in df.iterrows():
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
                    print(f"Warning: JSON file for company '{company_name}' not found. Skipping news for this company.")
                    missing_company_count += 1
                    continue # 회사 정보가 없으면 해당 뉴스 건너뛰기
                
                company = Company(name=company_name, data=company_data)
                db.add(company)
                db.flush() # ID를 얻기 위해 flush
                company_id = company.id
                company_map[company_name] = company_id # 새로 추가된 회사 맵에 반영
            
            # 미리 생성된 임베딩을 인덱스를 통해 가져옵니다.
            title_embedding = all_title_embeddings[index]

            # 임베딩이 비어있는지 확인 (generate_embedding에서 오류 시 빈 리스트 반환 가능성)
            if not title_embedding:
                print(f"Warning: Empty embedding for title: {row['title']}. Skipping this news item.")
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
                title_embedding=title_embedding,
                original_link=row['original_link'],
                news_date=news_date_obj
            )
            db.add(news_item)
            inserted_count += 1

            if inserted_count % 100 == 0:
                print(f"  - {inserted_count}개의 뉴스 데이터 삽입 중...")
        
        db.commit()
        print(f"Data insertion complete! Total inserted: {inserted_count}, Skipped (duplicate/empty embedding): {skipped_count}, Missing company: {missing_company_count}")
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
        print(traceback.format_exc()) # 상세한 traceback 출력
    finally:
        db.close()

# if __name__ == "__main__":
#     asyncio.run(insert_data()) # 비동기 함수를 실행하도록 변경
