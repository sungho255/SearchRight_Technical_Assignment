from pydantic import BaseModel
from datetime import date

class CompanyNewsSchema(BaseModel):
    id: int
    company_id: int
    title: str
    original_link: dict # JSON type in DB, so dict in Pydantic
    news_date: date

    model_config = {"from_attributes": True}