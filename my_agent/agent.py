from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Dict
from utils.nodes import noeud_initialisation, noeud_planification, noeud_recherche, noeud_redaction

class AgentState(TypedDict):
    utilisateur: Dict
    plan: List[str]
    sections_redigees: Dict
    etape_actuelle: str
    information: str

def graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("initialisation", noeud_initialisation)
    workflow.add_node("planification", noeud_planification)
    workflow.add_node("recherche", noeud_recherche)
    workflow.add_node("redaction", noeud_redaction)

    workflow.add_edge(START, "initialisation")
    workflow.add_edge("initialisation", "planification")
    workflow.add_edge("planification", "recherche")
    workflow.add_edge("recherche", "redaction")
    workflow.add_edge("redaction", END)

    return workflow.compile()