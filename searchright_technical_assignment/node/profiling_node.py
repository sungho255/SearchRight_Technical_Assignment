################################################## 라이브러리 #########################################################
# 기본 모듈 임포트
import os
import openai
import logging
from dotenv import load_dotenv

# LangChain 체인 관련 모듈 임포트
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


# 사용자 정의 모듈 임포트
from ..state.profiling_state import ProfilingState
from ..retriever.pgvector import search_by_keyword
from ..db.conn import get_db
from ..crud.company_dao import CompanyDAO
from ..model.company import Company
from ..schema.response_dto import LeadershipResponse, CompanySizeResponse, ExperienceResponse

# 경고 무시 설정
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
####################################################################################################################

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정 및 임베딩 모델 초기화
openai.api_key = os.getenv('OPENAI_API_KEY')
embeddings = OpenAIEmbeddings()


def input(state: ProfilingState):
    """
    LangGraph 워크플로우의 시작 노드입니다.
    입력 상태를 그대로 반환하여 다음 노드로 전달합니다.

    Args:
        state (ProfilingState): 현재 프로파일링 상태 정보를 포함하는 객체.

    Returns:
        ProfilingState: 변경되지 않은 프로파일링 상태 정보.
    """
    logger.info("초기 상태로 그래프 시작.")
    return state
    
# 1. 대학 수준 분별 노드
def college_level(state: ProfilingState, prompt: PromptTemplate):
    """
    지원자의 학력 정보를 기반으로 대학 수준을 판단하는 노드입니다.

    Args:
        state (ProfilingState): 현재 프로파일링 상태 정보를 포함하는 객체.
        prompt (PromptTemplate): 대학 수준 판단에 사용될 프롬프트 템플릿.

    Returns:
        dict: 'college_level' 키에 판단된 대학 수준을 포함하는 딕셔너리.
    """
    logger.info("대학 수준 노드 실행 중.")
    # 상태 변수에서 대학 정보 추출
    college = state['college']
    
    # 1. 모델 선언 (GPT-4o 사용)
    model = ChatOpenAI(model='gpt-4o', streaming=True, temperature=0)
    
    # 2. LLM과 문자열 출력 파서를 바인딩하여 체인 생성
    chain = prompt | model | StrOutputParser()

    # 3. 대학 수준 생성 LLM 실행
    answer = chain.invoke({'college' : college})
    logger.info(f"판단된 대학 수준: {answer}")
    
    return {'college_level':answer}


# 2. 리더십 유무 판단 노드
def leadership(state: ProfilingState, prompt: PromptTemplate):
    """
    지원자의 기술 및 직책 정보를 기반으로 리더십 유무를 판단하는 노드입니다.

    Args:
        state (ProfilingState): 현재 프로파일링 상태 정보를 포함하는 객체.
        prompt (PromptTemplate): 리더십 판단에 사용될 프롬프트 템플릿.

    Returns:
        dict: 'leadership' (리더십 유무) 및 'leadership_reason' (근거)를 포함하는 딕셔너리.
    """
    logger.info("리더십 노드 실행 중.")
    # 상태 변수에서 기술 및 직책 정보 추출
    skills = state['skills']
    titles = state['titles']
    
    # 1. 모델 선언 (GPT-4o 사용)
    model = ChatOpenAI(model='gpt-4o', streaming=True, temperature=0)
    
    # 2. 구조화된 출력을 위한 LLM 설정 (LeadershipResponse DTO 사용)
    llm_with_tool = model.with_structured_output(LeadershipResponse)
    
    # 3. LLM과 구조화된 출력 파서를 바인딩하여 체인 생성
    chain = prompt | llm_with_tool

    # 3. 리더십 판단 LLM 실행
    answer = chain.invoke({'skills' : skills, 'titles': titles})
    logger.info(f"판단된 리더십: {answer.leadership}")
    
    return {
        'leadership': answer.leadership,
        'leadership_reason': answer.reason
    }
    
# 3. 스타트업 기업 혹은 대기업 경험 판단 노드
def company_size(state: ProfilingState, prompt: PromptTemplate):
    """
    지원자의 경력 회사 정보를 기반으로 회사 규모 (스타트업/대기업)를 판단하는 노드입니다.
    데이터베이스에서 회사 정보를 조회하고, 필요한 경우 뉴스 검색을 통해 추가 정보를 얻습니다.

    Args:
        state (ProfilingState): 현재 프로파일링 상태 정보를 포함하는 객체.
        prompt (PromptTemplate): 회사 규모 판단에 사용될 프롬프트 템플릿.

    Returns:
        dict: 'company_size_and_reason' (회사 규모 및 근거)를 포함하는 딕셔너리.
    """
    logger.info("회사 규모 노드 실행 중.")
    # 상태 변수에서 회사 이름 및 근무 기간 정보 추출
    companynames_and_dates = state['companynames_and_dates']
    
    with get_db() as db_session:
        company_dao = CompanyDAO(db_session)
        matched_companies_results = company_dao.get_data_by_names(companynames_and_dates)
        
        # 각 회사별로 정보를 묶어서 리스트로 반환합니다.
        grouped_company_data = []
        for company_name, company_data in matched_companies_results:
            mae = None
            investment = None
            organization = None
            if isinstance(company_data, dict):
                mae = company_data.get('mae')
                investment = company_data.get('investment')
                organization = company_data.get('organization')
            
            grouped_company_data.append({
                "name": company_name,
                "mae": mae,
                "investment": investment,
                "organization": organization
            })

        # companynames_and_dates에 없는 기업명 추출
        companynames_and_dates_set = {item['companyName'] for item in companynames_and_dates if 'companyName' in item}
        grouped_company_data_names_set = {company_info['name'] for company_info in grouped_company_data}

        # 회사 이력에는 있지만 DB에 상세 정보가 없는 기업명 리스트
        companies_missing_db_info = list(companynames_and_dates_set - grouped_company_data_names_set)

        # companies_missing_db_info에 있는 기업명에 대해 PGVector 검색 수행
        company_news_contents = {}
        for company_name in companies_missing_db_info:
            # companynames_and_dates에서 해당 기업의 근무 기간 찾기
            start_end_dates_for_company = []
            for item in companynames_and_dates:
                if item.get('companyName') == company_name:
                    start_end_dates_for_company = item.get('startEndDates', [])
                    break
            
            # 각 근무 기간에 대해 뉴스 검색
            for date_range in start_end_dates_for_company:
                start_date = date_range.get('start')
                end_date = date_range.get('end')
                
                key_word = f"{company_name}의 투자 규모, 조직 규모"
                
                # search_by_keyword 함수 호출
                relevant_docs = search_by_keyword(key_word, k=5, start_date_obj=start_date, end_date_obj=end_date)

                if company_name not in company_news_contents:
                    company_news_contents[company_name] = []
                for doc in relevant_docs:
                    company_news_contents[company_name].append(doc.page_content)
        

        # 1. 모델 선언 (GPT-4o 사용)
        model = ChatOpenAI(model='gpt-4o', streaming=True, temperature=0)
        
        # 2. 구조화된 출력을 위한 LLM 설정 (CompanySizeResponse DTO 사용)
        llm_with_tool = model.with_structured_output(CompanySizeResponse)
        
        # 3. LLM과 구조화된 출력 파서를 바인딩하여 체인 생성
        chain = prompt | llm_with_tool

    
        # 4. 기업 경험 LLM 실행
        answer = chain.invoke({'companynames_and_dates' : companynames_and_dates, 'grouped_company_data' : grouped_company_data, 'company_news_contents': company_news_contents})
        logger.info(f"판단된 회사 규모: {answer.company_size_and_reason}")
    
        return {'company_size_and_reason':answer.company_size_and_reason}
    

# 4. 지원자 경험 판단 노드
def experience(state: ProfilingState, prompt: PromptTemplate):
    """
    지원자의 경력 설명을 기반으로 경험을 판단하는 노드입니다.
    데이터베이스에서 회사 제품 정보를 조회하여 판단에 활용합니다.

    Args:
        state (ProfilingState): 현재 프로파일링 상태 정보를 포함하는 객체.
        prompt (PromptTemplate): 경험 판단에 사용될 프롬프트 템플릿.

    Returns:
        dict: 'experience_and_reason' (경험 및 근거)를 포함하는 딕셔너리.
    """
    logger.info("경험 노드 실행 중.")
    # 상태 변수에서 설명 및 회사 이름/근무 기간 정보 추출
    descriptions = state['descriptions']
    companynames_and_dates = state['companynames_and_dates']
    
    with get_db() as db_session:
        company_dao = CompanyDAO(db_session)
        matched_companies_results = company_dao.get_data_by_names(companynames_and_dates)
        
        # 각 회사별로 정보를 묶어서 리스트로 반환합니다.
        grouped_company_data = []
        for company_name, company_data in matched_companies_results:
            products = None
            if isinstance(company_data, dict):
                products = company_data.get('products')
            
            grouped_company_data.append({
                "name": company_name,
                "products": products,
            })

        # 1. 모델 선언 (GPT-4o 사용)
        model = ChatOpenAI(model='gpt-4o', streaming=True, temperature=0)
        
        # 2. 구조화된 출력을 위한 LLM 설정 (ExperienceResponse DTO 사용)
        llm_with_tool = model.with_structured_output(ExperienceResponse)
        
        # 3. LLM과 구조화된 출력 파서를 바인딩하여 체인 생성
        chain = prompt | llm_with_tool

        
        # 4. 기업 경험 LLM 실행
        answer = chain.invoke({'descriptions' : descriptions, 'grouped_company_data' : grouped_company_data})
        logger.info(f"판단된 경험: {answer.experience_and_reason}")
        
        return {'experience_and_reason':answer.experience_and_reason}


    
def combine(state: ProfilingState):
    """
    다양한 노드에서 생성된 프로파일링 정보를 결합하여 최종 프로파일을 생성하는 노드입니다.

    Args:
        state (ProfilingState): 현재 프로파일링 상태 정보를 포함하는 객체.

    Returns:
        dict: 'profile' 키에 결합된 최종 프로파일을 포함하는 딕셔너리.
    """
    logger.info("결합 노드 실행 중.")
    profile = {}
    
    college_level = state.get('college_level')
    leadership = state.get('leadership')
    leadership_reason = state.get('leadership_reason')
    company_size_and_reason = state.get('company_size_and_reason')
    experience_and_reason = state.get('experience_and_reason')
    
    # college_level 처리
    if college_level != '최종학력없음':
        profile[college_level] = state.get('college')

    # leadership 처리
    if leadership != '리더쉽경험없음':
        profile[leadership] = leadership_reason
    
    # company_size 처리
    for company_size in company_size_and_reason:
        profile[company_size.company_size] = profile.get(company_size.company_size, []) + company_size.reasons

    
    # experience 처리
    for experience in experience_and_reason:
        profile[experience.experience] = experience.reasons

    logger.info(f"결합된 프로파일: {profile}")
    return {'profile': profile}