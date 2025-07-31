#########################################################################################
# 기본 모듈 임포트
import os
import pandas as pd
import traceback
import logging
# FastAPI 관련 모듈 임포트
from fastapi import APIRouter, status

# LangChain 관련 모듈 임포트
from langchain_core.runnables import RunnableConfig

# LangGraph 관련 모듈 임포트
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

## 사용자 정의 모듈 임포트
# 상태 정의 모듈
from searchright_technical_assignment.state.profiling_state import ProfilingState

# 워크플로우 정의 모듈
from searchright_technical_assignment.workflows.profiling_workflow import profilling_stategraph
# 기타 유틸리티 모듈
from searchright_technical_assignment.util.graph import visualize_graph
from searchright_technical_assignment.util.message import invoke_graph, random_uuid
from searchright_technical_assignment.util.extract_school_name import get_final_school_name
from searchright_technical_assignment.util.extract_titles import get_title
from searchright_technical_assignment.util.extract_companynames_and_dates import get_companynames_and_dates
from searchright_technical_assignment.util.extract_descriptions import get_descriptions
# 데이터 전송 객체 (DTO) 모듈
from searchright_technical_assignment.schema.talent_dto import TalentIn, TalentOut
#########################################################################################

# 로깅 설정
logger = logging.getLogger(__name__)

# APIRouter 인스턴스 생성
router = APIRouter()

# 프로파일링 엔드포인트
@router.post("/profilling", status_code = status.HTTP_200_OK, tags=['profilling'], response_model=TalentOut)
async def tech_langgraph(item: TalentIn):
    """
    지원자 프로파일링을 수행하는 비동기 함수입니다.

    Args:
        item (TalentIn): 지원자의 학력, 기술, 경력 정보를 포함하는 입력 데이터.

    Returns:
        TalentOut: 프로파일링 결과 및 상태 정보를 포함하는 출력 데이터.
    """
    logger.info('\n\u001b[36m[AI-API] \u001b[32m 프로파일링 시작\u001b[0m')
    try:
        # 워크플로우 그래프 생성
        workflow = profilling_stategraph(StateGraph(ProfilingState))

        # 체크포인터 설정
        memory = MemorySaver()

        # 그래프 컴파일
        app = workflow.compile(checkpointer=memory)

        # 그래프 시각화
        visualize_graph(app,'tech_graph')
        
        # config 설정 (재귀 최대 횟수, thread_id)
        config = RunnableConfig(recursion_limit=5, configurable={"thread_id": random_uuid()})

        # 지원자 정보 추출
        college = get_final_school_name(item.educations or [])
        skills = item.skills or []
        titles = get_title(item.positions or [])
        companynames_and_dates = get_companynames_and_dates(item.positions or [])
        descriptions = get_descriptions(item.positions or [])

        # State에 저장
        inputs = ProfilingState(college=college,
                                skills = skills,
                                titles = titles,
                                companynames_and_dates = companynames_and_dates,
                                descriptions = descriptions)

        # 그래프 실행 및 최종 상태 확인
        outputs = await app.ainvoke(inputs, config)
        
        logger.info("프로파일 생성 성공")
        return TalentOut(
            status="success",  # 응답 상태
            code=200,  # HTTP 상태 코드
            message="Profile 생성 완료",  # 응답 메시지
            output=outputs['profile'],
            node_timings={}
        )
    except Exception as e:
            logger.error(f"프로파일링 중 오류 발생: {e}")
            traceback.print_exc()
            return TalentOut(
                status="error",
                code=500,
                message=f"에러 발생: {str(e)}",
                output={},
                node_timings={}
            )