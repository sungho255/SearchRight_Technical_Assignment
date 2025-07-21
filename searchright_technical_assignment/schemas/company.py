from pydantic import BaseModel

class CompanySchema(BaseModel):
    id: int
    name: str
    data: dict

    model_config = {"from_attributes": True}