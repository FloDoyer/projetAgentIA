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
        utilisateur["date_debut"] = input("Date de début (ex: 1 mars 2026) : ")
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
    requete = f"Actualités et présentation de l'entreprise {entreprise} à {lieu}"
    resultats = tavily.search(query=requete, search_depth="advanced", max_results=3)
    info_web = "\n".join([res['content'] for res in resultats['results']])
    state["information"] = info_web
    state["etape_actuelle"] = "redaction"
    print("Recherche terminée et ajoutée au information.")
    sauvegarder_etat(state)
    return state





def noeud_redaction(state):
    """
    redaction du chapitre actuel.
    """
    print("\n PHASE REDACTION ")
    chapitre = state.get("chapitre_en_cours")
    information = state.get("information", "Aucune info web.")
    notes = state.get("notes_locales", "Aucune note de stage.")
    missions = state["utilisateur"].get("missions", "")
    prompt = f"""Tu es un expert en rédaction de rapports de stage de Master 2. 
    Ton objectif est de rédiger le chapitre suivant : "{chapitre}".
    DONNÉES DISPONIBLES :
    - Missions du stagiaire : {missions}
    - Notes: {notes}
    - information {information}
    CONSIGNES DE RÉDACTION :
    1. Utilise exclusivement le format Markdown (titres ##, gras **, listes -).
    2. Adopte un ton académique, professionnel et analytique.
    3. Fais le lien entre la théorie (web) et ta pratique (note).
    4. Si les notes sont riches, privilégie les détails techniques réels.
    5. Ne conclus pas le rapport, rédige seulement ce chapitre de manière fluide.
    """
    llm = ChatMistralAI(model="mistral-large-latest")
    reponse = llm.invoke(prompt)
    state["sections_redigees"][chapitre] = reponse.content
    sauvegarder_etat(state)
    return state

def noeud_reprise_section(state):
    """
    Analyse la progression et définit le chapitre actif dans le state.
    """
    print("\n ANALYSE DE LA PROGRESSION ")
    plan = state.get("plan", []) 
    rediges = state.get("sections_redigees", {})
    chapitre_suivant = None
    for chapitre in plan:
        if chapitre not in rediges:
            chapitre_suivant = chapitre
            break
    if chapitre_suivant:
        print(f"Nouveau chapitre détecté : {chapitre_suivant}")
        state["chapitre_en_cours"] = chapitre_suivant
        state["etape_actuelle"] = "analyse_besoin_infos"
    else:
        print("Tous les chapitres sont rédigés !")
        state["chapitre_en_cours"] = None
        state["etape_actuelle"] = "complet"
    sauvegarder_etat(state) 
    return state

def noeud_rapport_final(state):
    """Compile toutes les sections en un fichier final."""
    print("\nGÉNÉRATION DU RAPPORT FINAL ")
    entreprise = state["utilisateur"].get("entreprise", "Stage")
    nom_etudiant = state["utilisateur"].get("nom", "Étudiant")
    contenu_final = f"# Rapport de Stage - {entreprise}\n"
    contenu_final += f"**Auteur :** {nom_etudiant}\n\n"
    contenu_final += "---\n\n"
    for chapitre in state["plan"]:
        if chapitre in state["sections_redigees"]:
            contenu_final += f"## {chapitre}\n\n"
            contenu_final += f"{state['sections_redigees'][chapitre]}\n\n"
    nom_fichier = f"Rapport_{entreprise.replace(' ', '_')}.md"
    with open(nom_fichier, "w", encoding="utf-8") as f:
        f.write(contenu_final)
    print(f" Ton rapport est disponible ici : {nom_fichier}")
    state["etape_actuelle"] = "termine"
    sauvegarder_etat(state)
    return state    


def noeud_recherche_locale(state):
    """
    recherche dans tes notes de stage pour enrichir la rédaction.
    """
    chapitre = state.get("chapitre_en_cours")
    print(f"\n RECHERCHE NOTES pour : {chapitre}")
    notes_extraites = chercher_dans_journal(chapitre)
    state["notes_locales"] = notes_extraites
    state["etape_actuelle"] = "redaction"
    sauvegarder_etat(state)
    return state