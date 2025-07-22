# coordinator_agent.py
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import re

load_dotenv()


# client = Groq(
#             api_key=os.getenv("GROQ_API")
#               )
llm = ChatGroq(
    model_name="llama3-70b-8192",  # ou "mixtral-8x7b-32768" selon ton choix
    temperature=0,
    api_key=os.getenv("GROQ_API"),  # pense à configurer ta clé API Groq
)


def coordinator_agent(question: str) -> list[str]:
    """
    Analyse la question et retourne une liste des agents à appeler dans l'ordre.
    """
    # system_prompt = """
    # Tu es un orchestrateur intelligent pour un chatbot médical.
    # Ta tâche est de déterminer quels agents spécialisés doivent être sollicités
    # pour répondre efficacement à une question utilisateur.

    # - Agents disponibles :
    #   - clinical_trials
    #   - treatments
    #   - diagnosis
    #   - generaliste
    #   - scientific_summary

    # Donne une liste ordonnée d'agents pertinents.
    # Si plusieurs agents peuvent travailler en parallèle, regroupe-les dans un même bloc.
    # Exemple : [["clinical_trials", "treatments"], ["diagnosis"], ["generaliste"]]
    # """
    system_prompt = """
    Tu es un orchestrateur intelligent pour un chatbot médical.
    Ta tâche est de déterminer quels agents spécialisés doivent être sollicités
    pour répondre efficacement à une question utilisateur.

    - Agents disponibles :
    - clinical_trials (cherche des essais cliniques pertinents)
    - treatments (trouve des traitements adaptés)
    - diagnosis (aide à poser un diagnostic)
    - scientific_summary (fournit un résumé scientifique)
    - generaliste (répond de manière générale à tout type de question)

    ⚠️ Attention :
    - Évite d'ajouter 'generaliste' si les agents spécialisés suffisent à répondre.
    - Ajoute 'generaliste' **uniquement si aucun agent spécialisé n'est pertinent** ou si la question est très générale.
    - Donne une liste ordonnée d'agents pertinents.
    - Si plusieurs agents peuvent travailler en parallèle, regroupe-les dans un même bloc.

    Format attendu :
    Une liste Python du type :
    [["clinical_trials", "treatments"], ["diagnosis"]]

    Exemple :
    - Question : Quels sont les traitements pour le cancer du sein ?
    Réponse : [["treatments"]]

    - Question : Quels essais cliniques sont disponibles pour l'Alzheimer ?
    Réponse : [["clinical_trials"]]

    - Question : Quelle est la capitale de la France ?
    Réponse : [["generaliste"]]
    """

    prompt = f"{system_prompt}\n\nQuestion : {question}\nAgents :"
    response = llm.invoke(prompt)
    print(f"🧠 Coordinateur : {response.content}")

    # 🔥 Extraire la première liste trouvée
    match = re.search(r"\[\[.*?\]\]", response.content, re.DOTALL)
    if not match:
        raise ValueError("Aucune liste d'agents trouvée dans la réponse du coordinateur.")

    agents_list_str = match.group(0)
    print(f"✅ Liste extraite : {agents_list_str}")
    return eval(agents_list_str)

