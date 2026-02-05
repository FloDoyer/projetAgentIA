from utils.state import sauvegarder_etat

def noeud_initialisation(state):
    """Demande les infos à l'utilisateur si elles sont absentes du state."""
    print("\n PHASE D'INITIALISATION ")
    utilisateur = state.get("utilisateur", {})
    if not utilisateur.get("nom"):
        utilisateur["nom"] = input("Entrez votre nom et prénom : ")
    if not utilisateur.get("entreprise"):
        utilisateur["entreprise"] = input("Nom de l'entreprise : ")
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