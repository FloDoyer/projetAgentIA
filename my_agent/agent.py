from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, START, END

# Import des nœuds depuis ton dossier utils
from utils.nodes import (
    noeud_initialisation, 
    noeud_planification,
    noeud_reprise_section, 
    noeud_recherche, 
    noeud_redaction, 
    noeud_rapport_final,
    noeud_recherche_locale
)

# 1. Définition de l'état (AgentState)
class AgentState(TypedDict):
    utilisateur: Dict
    plan: List[str]
    sections_redigees: Dict
    contexte_recherche: str
    etape_actuelle: str
    chapitre_en_cours: str
    information: str
    notes_locales: str


def routeur_besoin_infos(state: AgentState):
    chapitre = state.get("chapitre_en_cours")
    chap_lower = chapitre.lower()
    if any(mot in chap_lower for mot in ["contexte", "présentation", "entreprise", "secteur"]):
        if not state.get("information"):
            return "recherche"
    if any(mot in chap_lower for mot in ["missions", "activités", "compétences", "bilan"]):
        return "local"
    
    return "redaction"

def routeur_logique_fin(state: AgentState):
    plan = state.get("plan", [])
    rediges = state.get("sections_redigees", {})
    if all(chapitre in rediges for chapitre in plan):
        return "complet"
    print(f"\nSection '{state.get('chapitre_en_cours')}' terminée.")
    reponse = input("Voulez-vous rédiger le chapitre suivant ? (oui/non) : ")
    if reponse.lower() == "oui":
        return "suivant"
    
    return "non"

def graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("initialisation", noeud_initialisation)
    workflow.add_node("planification", noeud_planification)
    workflow.add_node("reprise_section", noeud_reprise_section)
    workflow.add_node("noeud_recherche", noeud_recherche)
    workflow.add_node("noeud_chroma", noeud_recherche_locale) 
    workflow.add_node("redaction", noeud_redaction)
    workflow.add_node("rapport_final", noeud_rapport_final)

    workflow.add_edge(START, "initialisation")
    workflow.add_edge("initialisation", "planification")
    workflow.add_edge("planification", "reprise_section")
    workflow.add_conditional_edges("reprise_section", routeur_besoin_infos,
        {
            "recherche": "noeud_recherche",
            "local": "noeud_chroma",
            "redaction": "redaction"     
        }
    )
    workflow.add_edge("noeud_recherche", "redaction")
    workflow.add_edge("noeud_chroma", "redaction")
    workflow.add_conditional_edges("redaction", routeur_logique_fin,
        {
            "complet": "rapport_final",
            "suivant": "reprise_section",
            "non": END 
        }
    )
    workflow.add_edge("rapport_final", END)
    return workflow.compile()