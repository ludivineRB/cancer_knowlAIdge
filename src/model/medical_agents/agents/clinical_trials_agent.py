# import os
# import json

# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
# DATA_DIR = os.path.join(BASE_DIR, "data/raw/clinicaltrial")

# def load_trials():
#     trials = {}
#     for filename in os.listdir(DATA_DIR):
#         if filename.endswith(".json"):
#             cancer_type = filename.replace(".json", "").replace("_", "").lower()
#             with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
#                 trials[cancer_type] = json.load(f)
#     return trials

# TRIALS_DATA = load_trials()

# def clinical_trials_agent(question_en: str) -> str | None:
#     """
#     Recherche des essais cliniques si la question s'y prête.
#     Retourne une réponse formatée ou None si non pertinent.
#     """
#     question_lower = question_en.lower()

#     # 🔎 Vérifier si la question parle d’essais cliniques
#     keywords = ["clinical trial", "ongoing trial", "studies", "recruitment"]
#     if not any(kw in question_lower for kw in keywords):
#         return None

#     # 🩺 Déterminer le type de cancer
#     cancer_types = TRIALS_DATA.keys()
#     matched_type = None
#     for cancer in cancer_types:
#         if cancer in question_lower:
#             matched_type = cancer
#             break

#     if not matched_type:
#         return "❌ Sorry, I couldn’t identify the cancer type for clinical trials search."

#     trials = TRIALS_DATA[matched_type]
#     if not trials:
#         return f"ℹ️ No ongoing clinical trials found for {matched_type.title()} cancer."

#     # 📋 Formater les résultats
#     response_lines = [f"🧪 Ongoing clinical trials for **{matched_type.title()} cancer**:"]
#     for trial in trials[:5]:  # Limiter à 5 résultats
#         title = trial.get("title", "No title")
#         phase = trial.get("phase", "N/A")
#         url = trial.get("url", "No link")
#         response_lines.append(f"- **{title}** (Phase {phase}) → [Details]({url})")

#     return "\n".join(response_lines)

import os
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA_DIR = os.path.join(BASE_DIR, "data/raw/clinicaltrial")

# 📖 Charger les données
def load_trials():
    trials = {}
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            cancer_type = filename.replace(".json", "").replace("_", " ").lower()
            with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
                trials[cancer_type] = json.load(f)
    return trials

TRIALS_DATA = load_trials()

# 🩺 Synonymes pour une meilleure détection
CANCER_SYNONYMS = {
    "bowel cancer": "colorectal cancer",
    "lung tumour": "lung cancer",
    "breast tumour": "breast cancer",
    # Ajoute d’autres synonymes
}

def clinical_trials_agent(question_en: str) -> str | None:
    """
    Recherche des essais cliniques si la question s'y prête.
    Retourne une réponse formatée ou None si non pertinent.
    """
    question_lower = question_en.lower()

    # 🔄 Remplacer les synonymes dans la question
    for synonym, canonical in CANCER_SYNONYMS.items():
        if synonym in question_lower:
            question_lower = question_lower.replace(synonym, canonical)

    # 🔎 Vérifier si la question parle d’essais cliniques
    keywords = ["clinical trial", "ongoing trial", "studies", "recruitment"]
    if not any(kw in question_lower for kw in keywords):
        return None

    # 🩺 Déterminer le type de cancer
    cancer_types = TRIALS_DATA.keys()
    matched_type = None
    for cancer in cancer_types:
        if cancer in question_lower:
            matched_type = cancer
            break

    if not matched_type:
        return "❌ Sorry, I couldn’t identify the cancer type for clinical trials search."

    trials = TRIALS_DATA[matched_type]
    if not trials:
        return f"ℹ️ No ongoing clinical trials found for {matched_type.title()}."

    # 📋 Formater les résultats
    response_lines = [f"🧪 Ongoing clinical trials for **{matched_type.title()}**:"]
    for trial in trials[:5]:  # Limiter à 5 résultats
        title = trial.get("title", "No title")
        nct_id = trial.get("nctId", "N/A")
        url = f"https://clinicaltrials.gov/ct2/show/{nct_id}"
        response_lines.append(f"- **{title}** → [Details]({url})")

    return "\n".join(response_lines)
