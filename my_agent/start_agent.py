from utils.state import charger_etat
from agent import graph
from dotenv import load_dotenv
import sys

def lancement_agent():
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