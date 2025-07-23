#########################################################################################
# Basic
import os
import pandas as pd
import traceback
# Fastapi
from fastapi import APIRouter, HTTPException, status, File, UploadFile

# LangChain
from langchain_core.runnables import RunnableConfig

# Graph
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

## Module
# State
from searchright_technical_assignment.state.profiling_state import ProfilingState

# workflow
from searchright_technical_assignment.workflows.profiling_workflow import profilling_stategraph
# etc
from util.graph import visualize_graph
from util.message import invoke_graph, random_uuid
from util.extract_school_name import get_final_school_name
from util.extract_titles import get_title
# TechDTO
from schema.talent_dto import TalentIn, TalentOut
#########################################################################################
router = APIRouter()

# 대학 수준 Prompt
@router.post("/profilling", status_code = status.HTTP_200_OK, tags=['profilling'], response_model=TalentOut)
async def tech_langgraph(item: TalentIn):
    print('\n\033[36m[AI-API] \033[32m Profiling')
    try:
        workflow = profilling_stategraph(StateGraph(ProfilingState))

        # 5. 체크포인터 설정
        memory = MemorySaver()

        # 6. 그래프 컴파일
        app = workflow.compile(checkpointer=memory)

        # 7. 그래프 시각화
        visualize_graph(app,'tech_graph')
        
        # 8. config 설정(재귀 최대 횟수, thread_id)
        config = RunnableConfig(recursion_limit=5, configurable={"thread_id": random_uuid()})

        # 9. 지원자 정보 추출
        college = get_final_school_name(item.talent['educations'])
        skills = item.talent['skills']
        titles = get_title(item.talent['positions'])
        

        # 10. State에 저장
        inputs = ProfilingState(college=college,
                                skills = skills,
                                titles = titles,)

        # 11. 그래프 실행 출력
        invoke_graph(app, inputs, config)
 
        # 12. 최종 출력 확인 
        outputs = app.get_state(config)
        
        return {
            "status": "success",  # 응답 상태
            "code": 200,  # HTTP 상태 코드
            "message": "Profile 생성 완료",  # 응답 메시지
            'output': outputs.values['profile']
            
        }
    except Exception as e:
            traceback.print_exc()
            return {
                "status": "error",
                "code": 500,
                "message": f"에러 발생: {str(e)}",
                "output": {}
            }
