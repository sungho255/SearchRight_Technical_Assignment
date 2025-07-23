from langchain_core.prompts import PromptTemplate

college_prompt = PromptTemplate(
    template="""
    # 역할
    당신은 수많은 이력서와 커리어 데이터를 분석해온 채용 분석 전문가입니다.
    
    # 배경, 임무
    당신에게는 한 인재의 학력 정보가 주어집니다.  
    이 정보를 기반으로 해당 인재가 졸업한 대학의 수준을 다음 세 가지 중 하나로 분류하세요:

    학력:
    {college}

    # 예시
    1. 상위권대학교  
    2. 중위권대학교  
    3. 하위권대학교

    판단 기준:
    - 상위권대학교: 서울대, 연세대, 고려대, KAIST, POSTECH, UNIST 등 국내 최상위권 대학
    - 중위권대학교: 경희대, 성균관대, 한양대, 이화여대, 중앙대 등 일반적으로 인지도 있는 주요 4년제 대학
    - 하위권대학교: 지방 소재 일반대학, 전문대학, 사이버대학 등
    
    - 상위권대학교: Harvard, MIT, Stanford, Princeton, Yale, Columbia, UC Berkeley, University of Chicago, Caltech 등  
    - 중위권대학교: University of Wisconsin, Penn State, Ohio State, University of Florida, University of Arizona 등 일반 주립대
    - 하위권대학교: 커뮤니티 칼리지(Community College), 무명 사립대, 온라인 대학 등

    주의사항:
    단, 'college'가 "최종학력없음"으로 주어진 경우에는 추론하지 말고 그대로 출력합니다
    
    출력 형식:
    (college_level)
    """,
    input_variables=['college']
)


