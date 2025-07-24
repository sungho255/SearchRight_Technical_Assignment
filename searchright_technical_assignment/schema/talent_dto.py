from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TalentIn(BaseModel):
    educations: Optional[List[Dict[str, Any]]] = Field(default=None)
    skills: Optional[List[str]] = Field(default=None)
    positions: Optional[List[Dict[str, Any]]] = Field(default=None)

class TalentOut(BaseModel):
    status: str
    code: int
    message: str
    output: Dict

    model_config = {"from_attributes": True}
