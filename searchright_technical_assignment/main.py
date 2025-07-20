# Base
import os
from dotenv import load_dotenv

# FastAPI
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
#from fastapi.middleware.cors import CORSMiddleware

# DB

# Module
from DAO.comapnyDAO import CompanyDAO
from VO.company import Company

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()

class CompanySchema(BaseModel):
    id: int
    name: str
    data: dict

    class Config:
        orm_mode = True  # SQLAlchemy 모델을 Pydantic 모델로 변환할 수 있도록 설정

# 미들웨어
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
    return {"message": "Hello world from FastAPI1111111"}

@app.get("/companies/{company_id}", response_model=CompanySchema)
def get_company_by_id(company_id: int):
    dao = CompanyDAO()
    company = dao.get_by_id(company_id)
    dao.close()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company



print(f'Documents: http://localhost:8000/docs')

if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)