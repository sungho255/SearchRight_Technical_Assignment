# DB
from typing import TypedDict, Annotated, List, Dict

class ProfilingState(TypedDict):
    # 대학 수준
    college: Annotated[str, "대학"]
    college_level: Annotated[str, "대학 수준"]
    # 리더쉽
    skills: Annotated[List, "능력"]
    titles: Annotated[List, "포지션 제목"]
    leadership: Annotated[str, "리더쉽"]
    leadership_reason: Annotated[List, "리더쉽 근거"]
    # 회사 경험
    companynames_and_dates: Annotated[List, "근무 기업명과 근무 기간"]
    investment: Annotated[Dict,"투자 유치 시기 및 금액 (스타트업 여부 파악)"]
    organiztion: Annotated[Dict, "재직자 수 (규모 확인)"]
    company_size_and_reason: Annotated[List, "기업 규모"]
    # 경험
    descriptions: Annotated[List, "포지션 설명"]
    products: Annotated[Dict, "회사 제품/상품"]
    experience_and_reason: Annotated[List, "경험"]
    # Profile
    profile: Annotated[Dict, "프로파일"]
    