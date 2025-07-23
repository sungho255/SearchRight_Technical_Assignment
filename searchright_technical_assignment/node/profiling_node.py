################################################## LIBRARY #########################################################
# Basic
import os
import openai
from dotenv import load_dotenv

# Chain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Tool
from pydantic import BaseModel, Field

# DB
from typing import TypedDict, Annotated, List, Union

# Error
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Module
from state.profiling_state import ProfilingState
from retriever.pgvector import retriever
####################################################################################################################
################################################### STATE ########################################################### 청크 합치기
# 환경설정
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
embeddings = OpenAIEmbeddings()


def input(state: ProfilingState):
    """
    langgraph 시작 노드

    Args:
        state (QuestionState): 질문의 상태 정보를 포함하는 객체.

    Returns:
        QuestionState: 질문의 상태 정보 
    """
    return state
    
# 1. 대학 수준 분별 노드
def college_level(state: ProfilingState, prompt: PromptTemplate):
    # State 변수 선언 지정
    college = state['college']
    
    # 1. 모델 선언
    model = ChatOpenAI(model='gpt-4o', streaming=True, temperature=0)
    
    # 2. llm + PydanticOutputParser 바인딩 체인 생성
    chain = prompt | model | StrOutputParser()

    # 3. 대학 수준 생성 LLM 실행
    answer = chain.invoke({'college' : college})
    
    return {'college_level':answer}


# 리더십 정보 구조화
class LeadershipResponse(BaseModel):
    leadership: str = Field(description="리더십 경험 여부, 예: '리더쉽' 또는 '리더쉽경험없음'")
    reason: List[str] = Field(description="리더십 판단 근거 리스트")

# 2. 리더쉽 유무 판단 노드
def leadership(state: ProfilingState, prompt: PromptTemplate):
    # State 변수 선언 지정
    skills = state['skills']
    titles = state['titles']
    
    # 1. 모델 선언
    model = ChatOpenAI(model='gpt-4o', streaming=True, temperature=0)
    
    # 2. 구조화된 출력을 위한 LLM 설정
    llm_with_tool = model.with_structured_output(LeadershipResponse)
    
    # 3. llm + PydanticOutputParser 바인딩 체인 생성
    chain = prompt | llm_with_tool

    # 3. 대학 수준 생성 LLM 실행
    answer = chain.invoke({'skills' : skills, 'titles': titles})
    
    return {
        'leadership': answer.leadership,
        'leadership_reason': answer.reason
    }
    
# 2. 스타트업 기업 혹은 대기업 경험 판단 노드
# def company_size(state: ProfilingState, prompt: PromptTemplate):
#     # State 변수 선언 지정
#     company_names = state['company_names']
    
#     # investment: 
#     # organiztion: 
    
#     # 1. 모델 선언
#     model = ChatOpenAI(model='gpt-4o', streaming=True, temperature=0)
    
#     # 2. 구조화된 출력을 위한 LLM 설정
#     llm_with_tool = model.with_structured_output(LeadershipResponse)
    
#     # 3. llm + PydanticOutputParser 바인딩 체인 생성
#     chain = prompt | llm_with_tool

#     # 3. 대학 수준 생성 LLM 실행
#     answer = chain.invoke({'skills' : skills, 'titles': titles})
    
#     return {
#         'leadership': answer.leadership,
#         'leadership_reason': answer.reason
#     }

def combine(state: ProfilingState):
    profile = {}
    
    college = state['college']
    college_level = state['college_level']
    leadership = state['leadership']
    leadership_reason = state['leadership_reason']
    
    if college_level != '최종학력없음':
        profile[college] = college_level
    if leadership != '리더쉽경험없음':
        profile[leadership] = leadership_reason

    return {'profile': profile}
