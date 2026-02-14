from utils.state import charger_etat
from agent import graph
from dotenv import load_dotenv
import sys
import json

def reinitialiser_agent():
    confirm = input("Voulez-vous réinitialiser l'agent ? (oui/non) : ")
    if confirm.lower() == 'oui':
        etat_vide = {
            "utilisateur": {
                "nom": "",
                "entreprise": "",
                "missions": [],
                "date_debut": "",
                "lieu": "",
                "durée": ""
            },
            "plan": [],
            "sections_redigees": {},
            "etape_actuelle": "initialisation",
            "chapitre_en_cours": "",
            "information": "",
            "notes_locales": ""
        }
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(etat_vide, f, indent=4)
        print("agent réinitialisée.")
    

def lancement_agent():
    choix = input("Options : [1] Lancer l'agent | [2] Réinitialiser l'agent : ")
    if choix == "2":
        reinitialiser_agent()
        return
    load_dotenv()
    etat_initial = charger_etat()
    app = graph()
    print("Démarrage de l'agent...")
    app.invoke(etat_initial)
    print("Travail terminé pour cette session.")
    sys.exit(0)

if __name__ == "__main__":
    lancement_agent()
    #app = graph()
    #app.get_graph().draw_mermaid_png(output_file_path="graph_visu.png")