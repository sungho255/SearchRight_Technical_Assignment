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
from .routers import company_dto, companynews_dto

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()

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

# 회사  
app.include_router(company_dto.router)
# 회사 뉴스
app.include_router(companynews_dto.router)


print(f'Documents: http://localhost:8000/docs')

if __name__ == '__main__': 
    uvicorn.run("main:app", reload=True)