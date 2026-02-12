from langchain_mistralai import ChatMistralAI
from tavily import TavilyClient
from utils.state import sauvegarder_etat
from utils.db import chercher_dans_journal
import os

def noeud_initialisation(state):
    """Demande les infos à l'utilisateur si elles sont absentes du state."""
    print("\n PHASE D'INITIALISATION ")
    utilisateur = state.get("utilisateur", {})
    if not utilisateur.get("nom"):
        utilisateur["nom"] = input("Entrez votre nom et prénom : ")
    if not utilisateur.get("entreprise"):
        utilisateur["entreprise"] = input("Nom de l'entreprise : ")
    if not utilisateur.get("date_debut"):
        utilisateur["date_debut"] = input("Date de début (ex: 1er mars 2026) : ")
    if not utilisateur.get("lieu"):
        utilisateur["lieu"] = input("Lieu du stage (Ville) : ")
    if not utilisateur.get("durée"):
        utilisateur["durée"] = input("Durée du stage (ex: 6 mois) : ")
    if not utilisateur.get("missions"):
        print("Entrez vos missions (tapez 'fin' pour terminer) :")
        missions = []
        while True:
            m = input("- ")
            if m.lower() == 'fin': break
            missions.append(m)
        utilisateur["missions"] = missions
    state["utilisateur"] = utilisateur
    state["etape_actuelle"] = "planification"
    sauvegarder_etat(state)
    
    return state

def noeud_planification(state):
    """L'IA génère un plan basé sur les missions."""
    print("\n PHASE DE PLANIFICATION ")
    
    llm = ChatMistralAI(model="mistral-large-latest") 
    
    missions = ", ".join(state["utilisateur"]["missions"])
    entreprise = state["utilisateur"]["entreprise"]
    
    prompt = f"""Tu es un expert en rédaction académique. 
    L'étudiant a fait son stage chez {entreprise} sur les missions suivantes : {missions}.
    Génère un plan de rapport de stage en 4 chapitres logiques.
    Réponds uniquement avec les titres des chapitres séparés par des virgules."""
    
    reponse = llm.invoke(prompt)
    
    state["plan"] = [t.strip() for t in reponse.content.split(",")]
    state["etape_actuelle"] = "recherche" 
    
    print(f"Plan suggéré : {state['plan']}")
    sauvegarder_etat(state)
    return state

def noeud_recherche(state):
    """Utilise Tavily pour enrichir les informations avant la rédaction."""
    print("\n PHASE DE RECHERCHE ")
    
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    entreprise = state["utilisateur"]["entreprise"]
    lieu = state["utilisateur"]["lieu"]
    requete = query = f"Actualités et présentation de l'entreprise {entreprise} à {lieu}"
    resultats = tavily.search(query=requete, search_depth="advanced", max_results=3)
    info_web = "\n".join([res['content'] for res in resultats['results']])
    state["information"] = info_web
    state["etape_actuelle"] = "redaction"
    print("Recherche terminée et ajoutée au information.")
    sauvegarder_etat(state)
    return state





def noeud_redaction(state):
    chapitre_actuel = state["plan"][0] 
    print(f"\n RÉDACTION : {chapitre_actuel} ")
    notes_pertinentes = chercher_dans_journal(chapitre_actuel)
    information = state.get('information', '')
    prompt = f"""
    Rédige le chapitre : "{chapitre_actuel}".
    MES NOTES :
    {notes_pertinentes}
    INFOS ENTREPRISE :
    {information}
    CONSIGNE : Utilise les notes pour prouver tes dires par des exemples réels de mon stage.
    """
    llm = ChatMistralAI(model="mistral-large-latest")
    reponse = llm.invoke(prompt)
    state["sections_redigees"][chapitre_actuel] = reponse.content
    sauvegarder_etat(state)
    return state