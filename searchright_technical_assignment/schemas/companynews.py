from pydantic import BaseModel
from datetime import date

class CompanyNewsSchema(BaseModel):
    id: int
    company_id: int
    title: str
    title_embedding: list[float] | None = None # Add this line for vector embedding
    original_link: str # Changed from dict to str
    news_date: date

    model_config = {"from_attributes": True}

class CompanyNewsCreate(BaseModel):
    company_id: int
    title: str
    original_link: str # Changed from dict to str
    news_date: date