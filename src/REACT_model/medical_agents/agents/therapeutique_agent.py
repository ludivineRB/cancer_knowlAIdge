# from sentence_transformers import SentenceTransformer, util
# import os
# import json

# # Définir les chemins de base
# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
# DATA_DIR = os.path.join(BASE_DIR, "data/raw/cancergov")

# # Charger le modèle pour mesurer la similarité
# _model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# # Cache pour stocker les traitements chargés
# _treatments_cache = {}

# def load_treatments():
#     """Charge et met en cache tous les fichiers JSON de traitements"""
#     global _treatments_cache
#     if _treatments_cache:
#         return _treatments_cache  # déjà chargé

#     print(f"📂 Chargement des traitements depuis : {DATA_DIR}")
#     for filename in os.listdir(DATA_DIR):
#         if filename.endswith(".json"):
#             filepath = os.path.join(DATA_DIR, filename)
#             with open(filepath, encoding="utf-8") as f:
#                 data = json.load(f)
#                 key = filename.replace(".json", "")
#                 _treatments_cache[key] = {
#                     "title": data.get("title", key),
#                     "url": data.get("url", ""),
#                     "content": data.get("content", "")
#                 }
#     print(f"✅ {len(_treatments_cache)} traitements chargés en cache.")
#     return _treatments_cache


# # Charger une seule fois au démarrage
# TRIALS_DATA = load_treatments()


# def treatments_agent(question_en: str) -> str | None:
#     """
#     Cherche une réponse dans les traitements contre le cancer.
#     Si la question n’est pas pertinente, retourne None.
#     """
#     print("🔎 [agent] recherche traitements cliniques…")

#     # Vérification simple des mots-clés
#     keywords = ["treatment", "therapy", "drug", "cancer", "chemotherapy", "radiation"]
#     if not any(kw in question_en.lower() for kw in keywords):
#         print("⚠️ [agent] Question non pertinente pour treatments_agent.")
#         return None

#     # Encoder la question
#     question_embedding = _model.encode(question_en, convert_to_tensor=True)

#     best_score = 0.0
#     best_treatment = None
#     best_excerpt = None

#     for treatment_data in TRIALS_DATA.values():
#         content = treatment_data["content"]
#         sentences = content.split(". ")

#         # Encoder les phrases du traitement
#         sentence_embeddings = _model.encode(sentences, convert_to_tensor=True)

#         # Calculer la similarité entre la question et chaque phrase
#         similarities = util.cos_sim(question_embedding, sentence_embeddings)
#         max_score, max_idx = similarities.max().item(), similarities.argmax().item()

#         if max_score > best_score:
#             best_score = max_score
#             best_treatment = treatment_data
#             # On prend 2-3 phrases à partir de la plus proche
#             best_excerpt = ". ".join(sentences[max_idx:max_idx + 2])

#     if best_score < 0.4:  # seuil de pertinence
#         print("🚫 [agent] Aucun traitement pertinent trouvé (score faible).")
#         return None

#     # Construire la réponse formatée
#     response = f"""**{best_treatment['title']}**
# {best_excerpt.strip()}.

# 👉 [Read more]({best_treatment['url']})
# """
#     print(f"✅ [agent] Réponse trouvée avec score {best_score:.2f}")
#     return response

from sentence_transformers import SentenceTransformer, util
import os
import json

# Définir les chemins de base
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA_DIR = os.path.join(BASE_DIR, "data/raw/cancergov")

# Charger le modèle pour mesurer la similarité
_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# Cache pour stocker les traitements chargés
_treatments_cache = {}

def load_treatments():
    """Charge et met en cache tous les fichiers JSON de traitements"""
    global _treatments_cache
    if _treatments_cache:
        return _treatments_cache  # déjà chargé

    print(f"📂 Chargement des traitements depuis : {DATA_DIR}")
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
                key = filename.replace(".json", "")
                _treatments_cache[key] = {
                    "title": data.get("title", key),
                    "url": data.get("url", ""),
                    "content": data.get("content", "")
                }
    print(f"✅ {len(_treatments_cache)} traitements chargés en cache.")
    return _treatments_cache


# Charger une seule fois au démarrage
TRIALS_DATA = load_treatments()

def treatments_agent(question_en: str) -> str | None:
    """
    Cherche une réponse dans les traitements contre le cancer.
    Si la question n’est pas pertinente, retourne None.
    """
    print("🔎 [agent] recherche traitements cliniques…")

    # Vérification simple des mots-clés
    keywords = ["treatment", "therapy", "drug", "cancer", "chemotherapy", "radiation"]
    if not any(kw in question_en.lower() for kw in keywords):
        print("⚠️ [agent] Question non pertinente pour treatments_agent.")
        return None

    # Encoder la question
    question_embedding = _model.encode(question_en, convert_to_tensor=True)

    best_score = 0.0
    best_treatment = None

    for treatment_data in TRIALS_DATA.values():
        # ⚡️ Comparer uniquement avec le titre du traitement
        title = treatment_data["title"]
        title_embedding = _model.encode(title, convert_to_tensor=True)

        # Calculer la similarité entre la question et le titre
        similarity = util.cos_sim(question_embedding, title_embedding).item()

        if similarity > best_score:
            best_score = similarity
            best_treatment = treatment_data

    if best_score < 0.4:  # seuil de pertinence
        print("🚫 [agent] Aucun traitement pertinent trouvé (score faible).")
        return None

    # Construire la réponse complète
    response = f"""**{best_treatment['title']}**
{best_treatment['content'].strip()}

👉 [Read more]({best_treatment['url']})
"""
    print(f"✅ [agent] Réponse trouvée avec score {best_score:.2f}")
    return response
