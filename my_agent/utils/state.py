import json
import os

# Nom du fichier de sauvegarde défini dans ta roadmap
STATE_FILE = "state.json"

def charger_etat():
    """Charge l'état depuis le fichier JSON ou initialise un état vide."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Structure initiale basée sur ton besoin d'initialisation
        return {
            "utilisateur": {
                "nom": "",
                "entreprise": "",
                "missions": []
            },
            "plan": [],
            "sections_redigees": {},
            "etape_actuelle": "initialisation"
        }

def sauvegarder_etat(etat):
    """Sauvegarde l'état actuel dans le fichier JSON."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(etat, f, indent=4, ensure_ascii=False)
    print("--- État sauvegardé avec succès ---")