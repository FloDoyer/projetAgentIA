import json
import os

STATE_FILE = "state.json"

def charger_etat():
    """Charge l'état depuis le fichier JSON ou initialise un état vide."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
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

def sauvegarder_etat(etat):
    """Sauvegarde l'état actuel dans le fichier JSON."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(etat, f, indent=4, ensure_ascii=False)
    print(" État sauvegardé avec succès ")