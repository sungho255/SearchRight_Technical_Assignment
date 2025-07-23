# Graph
from langgraph.graph import END, StateGraph

# Node
from node.profiling_node import input, college_level, leadership, combine
# prompt
from prompt.profiling_prompt import college_prompt, leadership_prompt

def profilling_stategraph(workflow: StateGraph):
    # 1. Node 추가
    workflow.add_node("input", input)
    workflow.add_node("college_level", lambda state: college_level(state, prompt=college_prompt))
    workflow.add_node("leadership", lambda state: leadership(state, prompt=leadership_prompt))
    workflow.add_node("combine", combine)
    
    # 2. Edge 연결
    workflow.add_edge("input", "college_level")
    workflow.add_edge("input", "leadership")
    workflow.add_edge("college_level", "combine")
    workflow.add_edge("leadership", "combine")
    
    workflow.add_edge("combine", END)
    
    # 3. 그래프 진입점 설정
    workflow.set_entry_point("input")
    
    return workflow
