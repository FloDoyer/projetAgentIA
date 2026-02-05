from utils.state import charger_etat
from agent import graph

def lancement_agent():
    etat_initial = charger_etat()
    app = graph()
    print("Démarrage de l'agent...")
    app.invoke(etat_initial)
    print("Travail terminé pour cette session.")

if __name__ == "__main__":
    lancement_agent()