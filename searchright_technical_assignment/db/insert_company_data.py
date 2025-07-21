import os
import json
import glob
import traceback

from sqlalchemy.orm import Session
from sqlalchemy import exists
from searchright_technical_assignment.db.conn import SessionLocal
from searchright_technical_assignment.models.company import Company

def insert_company_data():
    db: Session = SessionLocal()
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        example_datas_dir = os.path.join(script_dir, '..', '..', 'example_datas')
        
        # 회사 데이터 파일 찾기
        company_files = glob.glob(os.path.join(example_datas_dir, "company_ex*.json"))
        print(f"총 {len(company_files)}개의 회사 데이터 파일을 찾았습니다.")

        inserted_count = 0
        skipped_count = 0

        for file_path in sorted(company_files):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    company_data = json.load(f)
                
                # 파일 이름에서 회사 이름 추출 (예: company_ex1_비바리퍼블리카.json -> 비바리퍼블리카)
                company_name = os.path.basename(file_path).split("_")[-1].split(".")[0]

                # 이미 존재하는지 확인
                company_exists = db.query(exists().where(Company.name == company_name)).scalar()

                if company_exists:
                    print(f"  - 회사 '{company_name}' 데이터가 이미 존재합니다. 건너뜁니다.")
                    skipped_count += 1
                else:
                    company = Company(name=company_name, data=company_data)
                    db.add(company)
                    db.flush() # ID를 얻기 위해 flush
                    print(f"  - 회사 '{company_name}' 데이터 삽입 중...")
                    inserted_count += 1

            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"  - 파일 로드 또는 JSON 파싱 오류 ({file_path}): {e}")
                continue
            except Exception as e:
                print(f"  - 회사 데이터 처리 중 예상치 못한 오류 ({file_path}): {e}")
                print(traceback.format_exc())
                continue

        db.commit()
        print(f"회사 데이터 삽입 완료! 총 삽입: {inserted_count}, 건너뜀: {skipped_count}")

    except Exception as e:
        db.rollback()
        print(f"An error occurred during company data insertion: {e}")
        print(traceback.format_exc())
    finally:
        db.close()

if __name__ == "__main__":
    insert_company_data()
