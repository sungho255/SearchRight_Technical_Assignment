from pydantic import BaseModel
from datetime import date

class CompanyNewsSchema(BaseModel):
    id: int
    company_id: int
    title: str
    chunk_index: int
    combined_embedding: list[float] | None = None # 벡터 임베딩을 위해 이 줄을 추가합니다
    original_link: str # Changed from dict to str
    news_date: date

    model_config = {"from_attributes": True}

class CompanyNewsCreate(BaseModel):
    company_id: int
    title: str
    original_link: str # Changed from dict to str
    news_date: date