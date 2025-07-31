from langchain_core.prompts import PromptTemplate

# 대학교 수준 분별 Prompt
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

# 리더쉽 Prompt
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

    # 주의사항:  
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

# 회사 경험 Prompt
company_size_prompt = PromptTemplate(
    template="""
    # 역할
    당신은 회사 정보와 근무 정보를 바탕으로 회사 규모를 분석하는 전문가입니다. 
    
    # 배경 및 임무 
    제공된 각 회사 정보(grouped_company_data)와 근무 정보(companynames_and_dates), 뉴스기사(company_news_contents)를 바탕으로 'companyName' 회사가 '대규모 회사 경험'인지 '성장기스타트업 경험'인지 판단하세요.

    # 입력 데이터
    다음 'grouped_company_data'는 회사의 정보를 'companynames_and_dates'는 근무회사명과 근무기간을 'company_news_contents'는 부족한 회사 정보의 뉴스기사 내용을 담고 있습니다. 각 필드의 의미는 다음과 같습니다:

    grouped_company_data:
    - name: 화사명
    - mae: 자본금 (단위: 원)
    - investment: 투자 단계 정보
    - organiztion: 재직자 수
    
    companynames_and_dates:
    - companyName: 근무회사명
    - startEndDates: 근무기간
    
    companynames_and_dates:
    {companynames_and_dates}
    grouped_company_data:
    {grouped_company_data}
    companynames_and_dates:
    {company_news_contents}

    # 분류 기준
    다음과 같은 경우 '성장기스타트업 경험'으로 판단합니다:
    - name에 ‘스타트업’, ‘랩스(Labs)’, ‘벤처’, ‘테크’, ‘소프트’ 등이 포함된 경우 (가능한 경우)
    - 근무기간 중 mae가 10억 원 이하일 경우
    - 근무기간 중 investment가 Series A ~ C 중 하나일 경우
    - 근무기간 중 organiztion 값이 10명 이상 300명 미만인 경우

    다음과 같은 경우 '대규모 회사 경험'으로 판단합니다:
    - name에 ‘주식회사’, ‘대우’, ‘현대’, ‘LG’, ‘삼성’, ‘KT’, ‘SK’ 등 대기업 계열 키워드가 포함된 경우 (가능한 경우)
    - mae가 100억 원 이상일 경우
    - investment가 None이거나 IPO, 상장, Pre-IPO 등으로 되어 있는 경우
    - organiztion 값이 300명 이상일 경우

    # 예시
    "대규모 회사 경험", ["삼성전자", "SKT"]
    "성장기스타트업 경험" ["토스 재직 시 투자 규모 2배 확장", "토스 재직 시 조직 2배 확장"]
    
    # 주의사항:
    1.'대규모회사경험'으로 분류한 경우 모든 'companynames_and_dates'의 name을 회사명에 포함하세요.
    2.'대규모회사경험'으로 분류한 경우 회사명을 리스트에 넣으세요.
    3.'성장 스타트업 경험'으로 분류한 경우 조직·투자 확대에 대한 내용을 리스트에 넣으세요.
    4.'성장 스타트업 경험'으로 분류한 경우 'company_news_contents'의 내용을 그대로 사용하지 말고 조직,규모,자본금에 대한 내용만 리스트에 넣으세요.
    
    # 출력 형식
    [
    (<대규모회사경험>, ["<회사명1>", "<회사명2>, ..."] or ["<조직·투자 확대1>", "<조직·투자 확대2>", ...]),
    (<대규모회사경험 or 성장스타트업경험>, ["<회사명1>", "<회사명2>, ..."] or ["<조직·투자 확대1>", "<조직·투자 확대2>", ...])
    ]
    
    """,
    input_variables=['companynames_and_dates', 'grouped_company_data','company_news_contents']
)

# 경험 Prompt
experience_prompt = PromptTemplate(
    template="""
    # 역할  
    당신은 지원자의 경력 정보와 기업의 정보를 바탕으로 지원자가 실질적인 경험을 보유했는지 판단하는 전문가입니다.

    # 배경 및 임무 
    제공된 각 회사 정보(grouped_company_data)와 경력 정보(descriptions)를 바탕으로 지원자가 어떤 경험을 보유했는지 판단하세요.

    # 입력 데이터
    다음 'grouped_company_data'는 회사의 정보를 'descriptions'는 경력 정보를 담고 있습니다. 각 필드의 의미는 다음과 같습니다:
    
    grouped_company_data:
    - products: 어떤 제품/서비스를 운영했는지, 어떤 도메인에서 일했는지 추론
    
    descriptions:
    {descriptions}
    grouped_company_data:
    {grouped_company_data}

    # 예시  
    - 'IPO', '밀리의 서재 재직 중 상장'
    - 'M&A 경험', '밀리의 서재 재직 중 지니뮤직에 매각'
    - '신규 투자 유치 경험', 'C level, Kasa Korea, LBox 투자 유치'
    - '대용량데이터처리경험', '네이버 하이퍼클로바 개발'
    - '음식 배달 플랫폼 도메인 경험', '요기요 주문 시스템 설계'

    # 주의사항   
    - 'descriptions'을 주로 판단할 것
    - 서로 다른 경험을 출력할 것.
    - 각 경험은 하나 씩만 출력할 것.
    - 경험 근거는 3단어로 표현할 것.
    - 경험 근거는 '개발', '매각', '인수'와 같은 동사로 끝날것.

    # 출력 형식
    [
    (<M&A 경험>, "<경험 근거>"),
    (<IPO 경험>, "<경험 근거>")
    ]
    """,
    input_variables=['descriptions','grouped_company_data']
)