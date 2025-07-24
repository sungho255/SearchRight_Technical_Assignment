from pydantic import Field, BaseModel
from typing import List

class LeadershipResponse(BaseModel):
    leadership: str = Field(description="leadership 여부")
    reason: List[str] = Field(description="근거 리스트")
    
class CompanySizeItem(BaseModel):
    company_size: str = Field(description="회사경험, 조직,투자 규모 or 회사명")
    reasons: List[str] = Field(description="근거 리스트")

class CompanySizeResponse(BaseModel):
    company_size_and_reason: List[CompanySizeItem] = Field(description="회사경험, 조직,투자 규모 or 회사명")
    
class ExperienceItem(BaseModel):
    experience: str = Field(description="경험")
    reasons: str = Field(description="근거")

class ExperienceResponse(BaseModel):
    experience_and_reason: List[ExperienceItem] = Field(description="경험")
    
