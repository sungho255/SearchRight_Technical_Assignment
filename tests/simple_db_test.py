import os
import sys

# 프로젝트 루트 디렉토리를 sys.path에 추가하여 모듈을 찾을 수 있도록 합니다.
# 현재 파일의 디렉토리 -> tests 디렉토리 -> 프로젝트 루트 디렉토리
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from searchright_technical_assignment.db.conn import get_db

def test_db_connection():
    """
    데이터베이스 연결을 시도하고 성공 여부를 출력하는 간단한 테스트 함수입니다.
    """
    print("데이터베이스 연결 테스트 시작...")
    try:
        with get_db() as db:
            # 간단한 쿼리를 실행하여 연결이 유효한지 확인
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
        print("데이터베이스 연결 성공!")
        return True
    except Exception as e:
        print(f"데이터베이스 연결 실패: {e}")
        return False

if __name__ == "__main__":
    test_db_connection()