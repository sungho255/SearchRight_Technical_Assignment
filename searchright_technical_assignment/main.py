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
from searchright_technical_assignment.router import company_router, companynews_router, profilling_router
from searchright_technical_assignment.util.colored_formatter import ColoredFormatter

# 로깅 설정
# 기본 로거를 가져옵니다.
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 모든 기존 핸들러를 제거합니다.
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# 새로운 스트림 핸들러를 생성하고 커스텀 포매터를 적용합니다.
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# 로거에 새로운 핸들러를 추가합니다.
logger.addHandler(ch)


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