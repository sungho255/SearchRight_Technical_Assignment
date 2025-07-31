import logging
import functools
# 그래프 관련 모듈 임포트
from langgraph.graph import END, StateGraph
# 노드 관련 모듈 임포트
from ..node.profiling_node import input, college_level, leadership, combine, company_size, experience
# 프롬프트 관련 모듈 임포트
from ..prompt.profiling_prompt import college_prompt, leadership_prompt, company_size_prompt, experience_prompt

# 로깅 설정
logger = logging.getLogger(__name__)

def profilling_stategraph(workflow: StateGraph):
    """
    프로파일링 워크플로우를 정의하는 LangGraph 상태 그래프를 설정합니다.

    Args:
        workflow (StateGraph): 노드와 엣지를 추가할 LangGraph의 StateGraph 인스턴스.

    Returns:
        StateGraph: 설정이 완료된 LangGraph 상태 그래프.
    """
    logger.info("프로파일링 상태 그래프 설정 시작.")
    # 1. 노드 추가
    workflow.add_node("input", input)
    workflow.add_node("college_level", functools.partial(college_level, prompt=college_prompt))
    workflow.add_node("leadership", functools.partial(leadership, prompt=leadership_prompt))
    workflow.add_node("company_size", functools.partial(company_size, prompt=company_size_prompt))
    workflow.add_node("experience", functools.partial(experience, prompt=experience_prompt))
    workflow.add_node("combine", combine)
    logger.info("그래프에 노드 추가 완료.")
    
    # 2. 엣지 연결
    workflow.add_edge("input", "college_level")
    workflow.add_edge("input", "leadership")
    workflow.add_edge("input", "company_size")
    workflow.add_edge("input", "experience")
    
    workflow.add_edge("college_level", "combine")
    workflow.add_edge("leadership", "combine")
    workflow.add_edge("company_size", "combine")
    workflow.add_edge("experience", "combine")
    
    workflow.add_edge("combine", END)
    logger.info("그래프에 엣지 연결 완료.")
    
    # 3. 그래프 진입점 설정
    workflow.set_entry_point("input")
    logger.info("진입점 'input'으로 설정 완료.")
    
    logger.info("프로파일링 상태 그래프 설정 완료.")
    return workflow