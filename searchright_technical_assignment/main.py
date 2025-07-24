# 기본 모듈 임포트
import os
from dotenv import load_dotenv
import logging

# FastAPI 관련 모듈 임포트
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
#from fastapi.middleware.cors import CORSMiddleware # CORS 미들웨어

# 데이터베이스 관련 모듈 (현재 사용되지 않음)

# 라우터 모듈 임포트
from router import company_router, companynews_router, profilling_router

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 현재 파일의 기본 디렉토리 설정 및 .env 파일 로드
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 미들웨어 설정
# CORS 정책
# origins = [
#     "*"
#     ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins = origins,
#     allow_credentials = True,
#     allow_methods = ["*"],
#     allow_headers = ["*"],
# )

@app.get("/")
def say_hello():
    """
    루트 경로 ("/")에 대한 GET 요청을 처리합니다.

    Returns:
        dict: "message" 키와 "Hello world from FastAPI" 값을 포함하는 딕셔너리.
    """
    logger.info("Health Check")
    return {"message": "Hello world from FastAPI"}

# 회사 관련 라우터 포함
app.include_router(company_router.router)
# 회사 뉴스 관련 라우터 포함
app.include_router(companynews_router.router)
# 프로파일링 관련 라우터 포함
app.include_router(profilling_router.router)

# 문서 URL 로깅
logger.info(f'문서: http://localhost:8000/docs')

# 애플리케이션 실행 (직접 실행 시 uvicorn 사용)
if __name__ == '__main__': 
    uvicorn.run("main:app", reload=True)