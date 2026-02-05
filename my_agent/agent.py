from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Dict
from utils.nodes import noeud_initialisation

class AgentState(TypedDict):
    utilisateur: Dict
    plan: List[str]
    sections_redigees: Dict
    etape_actuelle: str

def graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("initialisation", noeud_initialisation)

    workflow.add_edge(START, "initialisation")
   
    workflow.add_edge("initialisation", END)

    return workflow.compile()