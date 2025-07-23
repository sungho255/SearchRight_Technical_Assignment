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

leadership_prompt = PromptTemplate(
    template="""
    # 역할  
    당신은 사람의 경력 정보를 바탕으로 리더십 경험 유무를 판단하는 전문가입니다.

    # 배경 및 임무  
    아래에 제공된 `skills`와 `titles` 리스트를 참고하여, 해당 인물이 리더십 경험을 가지고 있는지 분석해주시기 바랍니다.

    skills:  
    {skills}

    titles:  
    {titles}

    # 예시 (출력 형식 참조)
    "리더쉽", ["챕터 리드", "테크 리드"]

    "리더쉽", ["CFO", "성장전략 팀장 경험"]

    "리더쉽", ["CPO 경험 다수", "창업"]

    주의사항:  
    1. 리더십 경험은 다음 중 하나 이상을 포함하는 경우로 간주합니다:
        - 팀장, PM, 리드 등의 팀 리더 역할
        - 의사결정 권한 및 구성원 간 조율 경험
        - 프로젝트를 주도했거나 주도적으로 기여한 경험
        - 멘토링 또는 타인의 성장을 도운 경험

    2. 만약 리더십 경험이 없다고 판단되면 다음과 같이 출력하세요:
        "리더쉽경험없음", ["없음"]
        
    3. 판단 근거에 '역할 수행' 혹은 '스킬 보유' 같은 단어를 붙이지 마세요.

    # 출력 형식:
    "<리더쉽 or 리더쉽경험없음>", ["<판단 근거1>", "<판단 근거2>", ...]
    
    """,
    input_variables=['skills','titles']
)


