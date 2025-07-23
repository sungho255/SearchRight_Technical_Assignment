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
from typing import TypedDict, Annotated, List

# Error
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Module
from searchright_technical_assignment.state.profiling_state import ProfilingState
from retriever.pgvector import retriever
from prompt.college import college_prompt
# from ..schema.college import CollegeDTO
# from etc.evaluator import GroundednessChecker
# from etc.validator import format_docs
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
    
# def retrieve_document(state: ProfilingState, collection_name: str, class_id: str):
#     """
#     문서 검색 노드

#     Args:
#         state (QuestionState): 질문의 상태 정보를 포함하는 객체.
#         collection_name (str): zilliz collection명 (예: "resume" 또는 "evaluation").
#         class_id (str): 지원자, 회사 고유 ID

#     Returns:
#         QuestionState: 질문의 상태 정보 
#     """
#     # 질문을 상태에서 가져옵니다.
#     latest_question = state[f"{collection_name}_query"]
#     state_class_id = state[f'{class_id}']
    
#     retriever = hybrid_retriever(collection_name,state_class_id,class_id)
    
#     # 문서에서 검색하여 관련성 있는 문서를 찾습니다.
#     retrieved_docs = retriever.invoke(latest_question)
#     # 검색한 chunk 저장
#     for chunk in retrieved_docs:
#         state['resume_chunk'].append(chunk.page_content)
#     # 검색된 문서를 형식화합니다.(프롬프트 입력으로 넣어주기 위함)
#     retrieved_docs = format_docs(retrieved_docs)
    
#     # 검색된 문서를 context 키에 저장합니다.
#     return retrieved_docs


# def experience_work_fact_checking(state: QuestionState, key: str):
#     """
#     경험 중심 또는 경력 중심 자소서의 질문과 문맥 간 관련성을 평가하는 함수.

#     Args:
#         state (QuestionState): 현재 질문의 상태를 저장하는 객체.
#         key (str): 관련성을 평가할 대상의 키값 (예: "resume" 또는 "evaluation").

#     Returns:
#         str: 관련성이 있는 경우 "yes", 관련성이 없는 경우 "no".
#     """
#     # 관련성 평가기를 생성합니다.
#     question_answer_relevant = GroundednessChecker(
#         llm=ChatOpenAI(model="gpt-4o", temperature=0), target="score-question-retrieval"
#     ).create()

#     # 관련성 체크를 실행("yes" or "no")
#     response = question_answer_relevant.invoke(
#         {"question": state[f'{key}_query'], "context1": state[key]}
#     )

#     print(f"==== [{key} CHECK] ====")
#     print(response.score)

#     # 참고: 여기서의 관련성 평가기는 각자의 Prompt 를 사용하여 수정할 수 있습니다. 여러분들의 Groundedness Check 를 만들어 사용해 보세요!
#     return response.score

def college_level(state: ProfilingState):
    # State 변수 선언 지정
    college = state['college']
    
    # 1. 모델 선언
    model = ChatOpenAI(model='gpt-4o', streaming=True, temperature=0)
    
    # 2. 구조화된 출력을 위한 LLM 설정
    # llm_with_tool = model.with_structured_output(CollegeDTO)
    
    # 3. llm + PydanticOutputParser 바인딩 체인 생성
    chain = college_prompt | model | StrOutputParser()

    # 4. 대학 수준 생성 LLM 실행
    answer = chain.invoke({'college' : college})
    
    print(f"Generated college_level: {college_level}")
    return {'college_level':answer}

def college_level(state: ProfilingState):
    # State 변수 선언 지정
    college = state['college']
    
    # 1. 모델 선언
    model = ChatOpenAI(model='gpt-4o', streaming=True, temperature=0)
    
    # 2. 구조화된 출력을 위한 LLM 설정
    # llm_with_tool = model.with_structured_output(CollegeDTO)
    
    # 3. llm + PydanticOutputParser 바인딩 체인 생성
    chain = college_prompt | model | StrOutputParser()

    # 4. 대학 수준 생성 LLM 실행
    answer = chain.invoke({'college' : college})
    
    print(f"Generated college_level: {college_level}")
    return {'college_level':answer}

