################################################## 라이브러리 #########################################################
# 기본 모듈 임포트
import os
import sys
import time
import openai
import asyncio
import logging
from dotenv import load_dotenv
from async_lru import alru_cache

# LangChain 체인 관련 모듈 임포트
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 프로젝트 루트 경로를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from searchright_technical_assignment.schema.response_dto import LeadershipResponse, CompanySizeResponse, ExperienceResponse
from searchright_technical_assignment.crud.company_dao import CompanyDAO
from searchright_technical_assignment.db.conn import get_db
from searchright_technical_assignment.model.company import Company
from searchright_technical_assignment.retriever.pgvector import search_by_keyword
from searchright_technical_assignment.state.profiling_state import ProfilingState
from searchright_technical_assignment.util.grouped_data_util import get_grouped_company_data

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

 # --- LLM 모델 및 구조화된 출력 객체 전역 초기화 (재사용) ---
# ChatOpenAI 모델은 한 번만 초기화
_global_chat_llm = ChatOpenAI(model='gpt-4o', streaming=True, temperature=0)
# 각 DTO에 바인딩된 LLM 객체도 한 번만 초기화
_global_leadership_llm_with_tool = _global_chat_llm.with_structured_output(LeadershipResponse)
_global_company_size_llm_with_tool = _global_chat_llm.with_structured_output(CompanySizeResponse)
_global_experience_llm_with_tool = _global_chat_llm.with_structured_output(ExperienceResponse)


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


def _to_hashable(obj):
    if isinstance(obj, dict):
        return tuple(sorted((k, _to_hashable(v)) for k, v in obj.items()))
    elif isinstance(obj, list):
        return tuple(_to_hashable(elem) for elem in obj)
    else:
        return obj

def _from_hashable(obj):
    if isinstance(obj, tuple) and all(isinstance(elem, tuple) and len(elem) == 2 for elem in obj) and all(isinstance(elem[0], str) for elem in obj):
        return {k: _from_hashable(v) for k, v in obj}
    elif isinstance(obj, tuple):
        return [_from_hashable(elem) for elem in obj]
    else:
        return obj

# 1. 대학 수준 분별 노드
async def college_level(state: ProfilingState, prompt: PromptTemplate):
    @alru_cache(maxsize=128)
    async def _get_college_level_answer(college_name: str, prompt_template_str: str):
        model = _global_chat_llm
        chain = PromptTemplate.from_template(prompt_template_str) | model | StrOutputParser()
        return await chain.ainvoke({'college' : college_name})
    """
    지원자의 학력 정보를 기반으로 대학 수준을 판단하는 노드입니다.

    Args:
        state (ProfilingState): 현재 프로파일링 상태 정보를 포함하는 객체.
        prompt (PromptTemplate): 대학 수준 판단에 사용될 프롬프트 템플릿.

    Returns:
        dict: 'college_level' 키에 판단된 대학 수준을 포함하는 딕셔너리.
    """
    start_time = time.time()
    logger.info("==> (1/4) college_level 노드 시작")
    
    logger.info("대학 수준 노드 실행 중.")
    # 상태 변수에서 대학 정보 추출
    college = state['college']
    
    # 1. 모델 선언 (GPT-4o 사용)
    model = _global_chat_llm
    
    # 2. LLM과 문자열 출력 파서를 바인딩하여 체인 생성
    chain = prompt | model | StrOutputParser()

    # 3. 대학 수준 생성 LLM 실행
    answer = await _get_college_level_answer(college, prompt.template)
    logger.info(f"판단된 대학 수준: {answer}")
    
    end_time = time.time()
    logger.info(f"<== (1/4) college_level 노드 종료 (소요 시간: {end_time - start_time:.2f}초)")
    
    return {'college_level':answer}

# 2. 리더십 유무 판단 노드
async def leadership(state: ProfilingState, prompt: PromptTemplate):
    @alru_cache(maxsize=128)
    async def _get_leadership_answer(skills_list: tuple, titles_list: tuple, prompt_template_str: str):
        llm_with_tool = _global_leadership_llm_with_tool
        chain = PromptTemplate.from_template(prompt_template_str) | llm_with_tool
        return await chain.ainvoke({'skills' : list(skills_list), 'titles': list(titles_list)})
    """
    지원자의 기술 및 직책 정보를 기반으로 리더십 유무를 판단하는 노드입니다.

    Args:
        state (ProfilingState): 현재 프로파일링 상태 정보를 포함하는 객체.
        prompt (PromptTemplate): 리더십 판단에 사용될 프롬프트 템플릿.

    Returns:
        dict: 'leadership' (리더십 유무) 및 'leadership_reason' (근거)를 포함하는 딕셔너리.
    """
    start_time = time.time() 
    logger.info("==> (2/4) leadership 노드 시작")
    
    logger.info("리더십 노드 실행 중.")
    # 상태 변수에서 기술 및 직책 정보 추출
    skills = state['skills']
    titles = state['titles']
    
    # 1. 모델 선언 (GPT-4o 사용)
    # model = _global_chat_llm
    
    # 2. 구조화된 출력을 위한 LLM 설정 (LeadershipResponse DTO 사용)
    llm_with_tool = _global_leadership_llm_with_tool
    
    # 3. LLM과 구조화된 출력 파서를 바인딩하여 체인 생성
    chain = prompt | llm_with_tool

    # 3. 리더십 판단 LLM 실행
    answer = await _get_leadership_answer(tuple(skills), tuple(titles), prompt.template)
    logger.info(f"판단된 리더십: {answer.leadership}")
    
    end_time = time.time()
    logger.info(f"<== (2/4) leadership 노드 종료 (소요 시간: {end_time - start_time:.2f}초)")
    
    return {
        'leadership': answer.leadership,
        'leadership_reason': answer.reason
    }
    
# 3. 스타트업 기업 혹은 대기업 경험 판단 노드
async def company_size(state: ProfilingState, prompt: PromptTemplate):
    @alru_cache(maxsize=512)
    async def _get_company_size_answer(companynames_and_dates_hashable: tuple, prompt_template_str: str):
        """
        회사 규모 판단을 위한 LLM 호출 및 관련 데이터 처리를 수행하는 캐시 가능한 헬퍼 함수.
        해시 가능한 형태로 변환된 회사 이름 및 날짜 정보와 프롬프트 템플릿 문자열을 인자로 받습니다.
        """
        companynames_and_dates = _from_hashable(companynames_and_dates_hashable)

        async with get_db() as db_session:
            company_dao = CompanyDAO(db_session)
            matched_companies_results = await company_dao.get_data_by_names(companynames_and_dates)
                
            matched_companies_map = {name: data for name, data in matched_companies_results}
            companynames_and_dates_map = {item['companyName']: item for item in companynames_and_dates if 'companyName' in item}

            grouped_company_data = []
            companies_missing_db_info = []
            
            for company_name, company_info in companynames_and_dates_map.items():
                if company_name in matched_companies_map:
                    grouped_company_data.append(get_grouped_company_data([company_info], [(company_name, matched_companies_map[company_name])])[0])
                else:
                    companies_missing_db_info.append(company_name)

            company_news_contents = {}
            tasks = []
            for company_name in companies_missing_db_info:
                start_end_dates_for_company = companynames_and_dates_map.get(company_name, {}).get('startEndDates', [])
                
                for date_range in start_end_dates_for_company:
                    start_date = date_range.get('start')
                    end_date = date_range.get('end')
                    key_word = f"{company_name}의 투자 규모, 조직 규모"
                    tasks.append(search_by_keyword(key_word, k=3, start_date_obj=start_date, end_date_obj=end_date))
            
            all_relevant_docs = await asyncio.gather(*tasks)

            doc_index = 0
            for company_name in companies_missing_db_info:
                start_end_dates_count = len(companynames_and_dates_map.get(company_name, {}).get('startEndDates', []))
                company_news_contents[company_name] = []
                for _ in range(start_end_dates_count):
                    if doc_index < len(all_relevant_docs):
                        company_news_contents[company_name].extend(all_relevant_docs[doc_index])
                        doc_index += 1
                    else:
                        break
            
            llm_with_tool = _global_company_size_llm_with_tool
            chain = PromptTemplate.from_template(prompt_template_str) | llm_with_tool
            
            answer = await chain.ainvoke({'companynames_and_dates' : companynames_and_dates, 'grouped_company_data' : grouped_company_data, 'company_news_contents': company_news_contents})
            return answer
    """
    지원자의 경력 회사 정보를 기반으로 회사 규모 (스타트업/대기업)를 판단하는 노드입니다.
    데이터베이스에서 회사 정보를 조회하고, 필요한 경우 뉴스 검색을 통해 추가 정보를 얻습니다.

    Args:
        state (ProfilingState): 현재 프로파일링 상태 정보를 포함하는 객체.
        prompt (PromptTemplate): 회사 규모 판단에 사용될 프롬프트 템플릿.

    Returns:
        dict: 'company_size_and_reason' (회사 규모 및 근거)를 포함하는 딕셔너리.
    """
    start_time = time.time()
    logger.info("==> (3/4) company_size 노드 시작")
    logger.info("회사 규모 노드 실행 중.")
    
    # 상태 변수에서 회사 이름 및 근무 기간 정보 추출
    companynames_and_dates = state['companynames_and_dates']
    
    # companynames_and_dates를 해시 가능한 튜플로 변환 (캐싱을 위해)
    companynames_and_dates_hashable = _to_hashable(companynames_and_dates)

    answer = await _get_company_size_answer(companynames_and_dates_hashable, prompt.template)
    logger.info(f"판단된 회사 규모: {answer.company_size_and_reason}")

    end_time = time.time()
    logger.info(f"<== (3/4) company_size 노드 종료 (소요 시간: {end_time - start_time:.2f}초)")   

    return {'company_size_and_reason':answer.company_size_and_reason}
    
# 4. 지원자 경험 판단 노드
async def experience(state: ProfilingState, prompt: PromptTemplate):
    @alru_cache(maxsize=512)
    async def _get_experience_answer(descriptions_hashable: tuple, companynames_and_dates_hashable: tuple, prompt_template_str: str):
        """
        경험 판단을 위한 LLM 호출 및 관련 데이터 처리를 수행하는 캐시 가능한 헬퍼 함수.
        해시 가능한 형태로 변환된 설명, 회사 이름 및 날짜 정보와 프롬프트 템플릿 문자열을 인자로 받습니다.
        """
        descriptions = _from_hashable(descriptions_hashable)
        companynames_and_dates = _from_hashable(companynames_and_dates_hashable)

        async with get_db() as db_session:
            company_dao = CompanyDAO(db_session)
            matched_companies_results = await company_dao.get_data_by_names(companynames_and_dates)
            
            grouped_company_data = []
            for company_name, company_data in matched_companies_results:
                products = None
                if isinstance(company_data, dict):
                    raw_products = company_data.get('products', [])
                    products = [p.get('name') for p in raw_products if p.get('name')]
                
                grouped_company_data.append({
                    "name": company_name,
                    "products": products,
                })

            llm_with_tool = _global_experience_llm_with_tool
            chain = PromptTemplate.from_template(prompt_template_str) | llm_with_tool

            answer = await chain.ainvoke({'descriptions' : descriptions, 'grouped_company_data' : grouped_company_data})
            return answer
    """
    지원자의 경력 설명을 기반으로 경험을 판단하는 노드입니다.
    데이터베이스에서 회사 제품 정보를 조회하여 판단에 활용합니다.

    Args:
        state (ProfilingState): 현재 프로파일링 상태 정보를 포함하는 객체.
        prompt (PromptTemplate): 경험 판단에 사용될 프롬프트 템플릿.

    Returns:
        dict: 'experience_and_reason' (경험 및 근거)를 포함하는 딕셔너리.
    """
    start_time = time.time()
    logger.info("==> (4/4) experience 노드 시작")
    
    logger.info("경험 노드 실행 중.")
    # 상태 변수에서 설명 및 회사 이름/근무 기간 정보 추출
    descriptions = state['descriptions']
    companynames_and_dates = state['companynames_and_dates']
    
    descriptions_hashable = _to_hashable(descriptions)
    companynames_and_dates_hashable = _to_hashable(companynames_and_dates)

    answer = await _get_experience_answer(descriptions_hashable, companynames_and_dates_hashable, prompt.template)
    # logger.info(f"판단된 경험: {answer.experience_and_reason}")
    
    end_time = time.time()
    logger.info(f"<== (4/4) experience 노드 종료 (소요 시간: {end_time - start_time:.2f}초)")

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

    # logger.info(f"결합된 프로파일: {profile}")
    return {'profile': profile}