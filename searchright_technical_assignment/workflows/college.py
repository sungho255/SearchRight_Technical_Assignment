# Graph
from langgraph.graph import END, StateGraph

# Node
from searchright_technical_assignment.node.profiling_node import input, college_level
# etc
# from etc.validator import question_is_relevant, question_is_fact
from prompt.college import college_prompt

def profilling_stategraph(workflow: StateGraph):
    # 1. Node 추가
    workflow.add_node("input", input)
    workflow.add_node("college_level", college_level)
    
    # 2. Edge 연결
    workflow.add_edge("input", "college_level")
    workflow.add_edge("college_level", END)
    
    # 4. 그래프 진입점 설정
    workflow.set_entry_point("input")
    
    return workflow
