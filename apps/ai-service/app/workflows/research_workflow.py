from langgraph.graph import END, StateGraph
from typing import TypedDict


class AgentState(TypedDict):
    user_query: str
    context: list[str]
    plan: list[str]
    results: list[dict]
    current_step: str
    response: str


def build_research_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node("classify", _classify_query)
    workflow.add_node("plan", _create_plan)
    workflow.add_node("execute", _execute_plan)
    workflow.add_node("synthesize", _synthesize_results)

    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "plan")
    workflow.add_edge("plan", "execute")
    workflow.add_edge("execute", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()


def _classify_query(state: AgentState) -> dict:
    return {"current_step": "classified"}


def _create_plan(state: AgentState) -> dict:
    return {"plan": ["step1", "step2"]}


def _execute_plan(state: AgentState) -> dict:
    return {"results": []}


def _synthesize_results(state: AgentState) -> dict:
    return {"response": "Synthesized response"}
