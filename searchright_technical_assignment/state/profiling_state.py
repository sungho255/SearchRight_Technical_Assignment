# DB
from typing import TypedDict, Annotated, List, Dict

class ProfilingState(TypedDict):
    college: Annotated[str, "대학"]
    college_level: Annotated[str, "대학 수준"]
    skills: Annotated[List, "능력"]
    titles: Annotated[List, "포지션 제목"]
    leadership: Annotated[str, "리더쉽"]
    leadership_reason: Annotated[List, "리더쉽 근거"]
    company_names: Annotated[List, "기업 리스트"]
    investment: Annotated[Dict,"투자 유치 시기 및 금액 (스타트업 여부 파악)"]
    organiztion: Annotated[Dict, "재직자 수 (규모 확인)"]
    company_size: Annotated[str, "기업 규모"]
    
    profile: Annotated[Dict, "프로파일"]
    