# # orchestrateur.py
# from langchain_openai import ChatOpenAI
# from langgraph.graph import StateGraph, START, END
# from googletrans import Translator
# from ..agents.generaliste_agent import generaliste_agent
# from ..agents.clinical_trials_agent import clinical_trials_agent
# from ..agents.therapeutique_agent import treatments_agent
# # from ..agents.diagnostic_agent import diagnostic_agent
# from ..agents.summarize_pubmed_agent import summarize_pubmed_results
# from ..agents.conversational_agent import diagnostic_agent_conversation
# from ..agents.coordinator_agent import coordinator_agent
# from dotenv import load_dotenv
# import os
# import asyncio
# from pydantic import BaseModel


# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# # Google Translate
# translator = Translator()

# class ChatState(BaseModel):
#     input: str
#     translated_input: str | None = None
#     language: str | None = None
#     answer_en: str | None = None
#     output: str | None = None
#     terminated: bool = False # Flag Stop
#     agent_sequence: list | None = None

# def translate_sync(text, dest="en"):
#     loop = asyncio.get_event_loop()
#     return loop.run_until_complete(translator.translate(text, dest=dest))

# # 🌍 Agent de traduction vers anglais
# def translate_to_english_node(state: ChatState) -> ChatState:
#     user_input = state.input
#     print("🌍 Traduction en anglais en cours...")

#     # ✅ Traduction synchrone
#     result = translate_sync(user_input, dest="en")

#     print(f"✅ Traduction anglaise : {result.text} (langue détectée : {result.src})")
#     state.translated_input = result.text
#     state.language = result.src
#     return state

# def coordinator_node(state: ChatState) -> ChatState:
#     question_en = state.translated_input or state.input
#     print("🧠 [coordinateur] Analyse de la question...")
#     agents_sequence = coordinator_agent(question_en)
#     state.agents_sequence = agents_sequence  # Stocke la séquence pour la suite
#     return state

# # 1. Fonction qui traite la question
# def generaliste_node(state: ChatState) -> ChatState:
#     question_en = state.translated_input or state.input
#     print(f"🔍 [node] question reçue (anglais) : {question_en}")

#     # answer = generaliste_agent(question_en)

#     print(f"✅ [node] réponse générée (anglais) : {answer}")
#     state.answer_en = answer
#     return state

# def clinical_trials_node(state: ChatState) -> ChatState:
#     question_en = state.translated_input or state.input
#     print(f"🔎 [node] recherche essais cliniques pour : {question_en}")

#     response = clinical_trials_agent(question_en)
#     if response:
#         # print(f"✅ [node] essais cliniques trouvés : {response}")
#         state.answer_en = response
#         # 👉 On saute le generaliste si on a trouvé une réponse
#         return state
#     else:
#         print("➡️ [node] pas d’essais cliniques détectés, on continue")
#         return state

# def treatments_node(state: ChatState) -> ChatState:
#     question_en = state.translated_input or state.input
#     print(f"🔎 [node] recherche de traitements pour : {question_en}")

#     response = treatments_agent(question_en)
#     if response:
#         # print(f"✅ [node] traitements trouvés : {response}")
#         state.answer_en = response
#         # 👉 On saute le generaliste si on a trouvé une réponse
#         return state
#     else:
#         print("➡️ [node] pas de traitements trouvés, on continue")
#         return state

# # def diagnosis_node(state: dict) -> dict:
# #     question_en = state.translated_input or state.input
# #     print("🔎 [graph] Appel de l'agent diagnostic Groq…")

# #     result = diagnostic_agent(question_en)
# #     # Retourne sous forme d'état LangGraph
# #     if result and "diagnosis" in result:
# #         print("✅ [agent] Diagnostic généré par Groq.")
# #         state.answer_en = result["diagnosis"]
# #     else:
# #         print("❌ [agent] Aucun diagnostic trouvé.")
# #     return state

# def diagnosis_node(state: ChatState) -> ChatState:
#     # Premier prompt déjà traduit en anglais
#     question_en = state.translated_input or state.input
#     user_language = state.language or "en"

#     print("🩺 [agent] Diagnostic interactif en cours…")

#     while True:
#         # 💬 Appelle l'agent de diagnostic en anglais
#         response_en = diagnostic_agent_conversation(question_en)
#         print(f"🤖 [agent EN] {response_en}")

#         # 🌍 Retraduit la réponse dans la langue d’origine
#         if user_language != "en":
#             result = translate_sync(response_en, dest=user_language)
#             response_translated = result.text
#             print(f"🌍 [agent {user_language.upper()}] {response_translated}")
#         else:
#             response_translated = response_en

#         # 🔚 Vérifie si le diagnostic est terminé
#         if "diagnostic final" in response_en.lower() or "je pense que" in response_en.lower():
#             print("✅ [agent] Diagnostic finalisé.")
#             state.answer_en = response_en  # On stocke l'EN pour la suite
#             break

#         # 👤 Demande la réponse suivante à l’utilisateur
#         user_input = input("👤 Votre réponse (ou 'exit' pour quitter) : ")
#         if user_input.lower() in ["exit", "quit", "stop"]:
#             print("🛑 Fin de la session de diagnostic.")
#             state.terminated = True
#             break

#         # 🌍 Détecte la langue et traduit en anglais
#         result = translate_sync(user_input, dest="en")
#         question_en = result.text
#         user_language = result.src  # Met à jour la langue détectée

#     return state

# def scientific_summary_node(state: ChatState) -> ChatState:
#     question_en = state.translated_input or state.input
#     user_language = state.language or "en"

#     print(f"📚 Recherche scientifique PubMed pour : {question_en}")
#     response = summarize_pubmed_results(query=question_en, language=user_language)

#     state.answer_en = response
#     return state

# # 🌍 Agent de traduction retour vers la langue d’origine
# def translate_to_original_language_node(state: ChatState) -> ChatState:
#     if not state.answer_en:
#         print("⚠️ Pas de réponse en anglais trouvée, on utilise directement la sortie existante.")
#         state.output = "❌ Une erreur est survenue."
#         return state

#     if state.language == "en":
#         state.output = state.answer_en
#         return state

#     # print(f"🌍 Retraduction en {state.language} en cours...")
#     result = translate_sync(state.answer_en, dest=state.language)
#     # print(f"✅ Réponse retraduite : {result.text}")
#     state.output = result.text
#     return state

# def finalize_output_node(state: ChatState) -> ChatState:
#     state.output = state.answer_en or "❌ Aucune réponse générée."
#     return state

# # 2. Création du graphe
# workflow = StateGraph(ChatState)
# # graph = StateGraph(state_schema=ChatState)


# # Ajoute les nœuds
# workflow.add_node("translate_to_english", translate_to_english_node)
# workflow.add_node("clinical_trials", clinical_trials_node)
# workflow.add_node("treatments", treatments_node)
# workflow.add_node("diagnosis", diagnosis_node)
# workflow.add_node("generaliste", generaliste_node)
# workflow.add_node("scientific_summary", scientific_summary_node)
# workflow.add_node("finalize_output", finalize_output_node)
# workflow.add_node("translate_to_original_language", translate_to_original_language_node)

# # Connexions entre les nœuds
# workflow.add_edge(START, "translate_to_english")
# workflow.add_edge("translate_to_english", "clinical_trials")
# workflow.add_conditional_edges(
#     "clinical_trials",
#     lambda state: "translate_to_original_language" if state.answer_en is not None else "treatments",
#     {
#       "translate_to_original_language": "translate_to_original_language",
#       "treatments": "treatments"
#     }
# )
# workflow.add_conditional_edges(
#     "treatments",
#     lambda state: "translate_to_original_language" if state.answer_en is not None else "scientific_summary",
#     {
#       "translate_to_original_language": "translate_to_original_language",
#       "scientific_summary": "scientific_summary"
#     }
# )
# workflow.add_edge("scientific_summary", "translate_to_original_language")
# workflow.add_conditional_edges(
#     "diagnosis",
#     lambda state: "translate_to_original_language" if state.answer_en is not None or state.terminated else "generaliste",
#     {
#       "translate_to_original_language": "translate_to_original_language",
#       "generaliste": "generaliste"
#     }
# )
# # workflow.add_edge("translate_to_english", "generaliste")
# workflow.add_edge("generaliste", "translate_to_original_language")
# workflow.add_edge("translate_to_original_language", "finalize_output")
# workflow.add_edge("translate_to_original_language", END)

# graph = workflow.compile()

# # 3. Boucle interactive
# if __name__ == "__main__":
#     llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=OPENAI_API_KEY)

#     print("👩‍⚕️ Chatbot médical (LangGraph v0.0.54+)")
#     while True:
#         question = input("👤 Question : ")
#         if question.lower() in ["exit", "quit", "q"]:
#             print("👋 À bientôt !")
#             break

#         # Invocation : tu dois fournir tout le State initial, ici 'input'
#         result = graph.invoke({"input": question})
#         # Résultat : dictionnaire avec la clé 'output'
#         print(f"🤖 Réponse : {result['output']}\n")


# ===================================================================================
# ===================================================================================
from langgraph.graph import StateGraph, START, END
from googletrans import Translator
from ..agents.generaliste_agent import generaliste_agent
from ..agents.clinical_trials_agent import clinical_trials_agent
from ..agents.therapeutique_agent import treatments_agent
from ..agents.summarize_pubmed_agent import summarize_pubmed_results
from ..agents.conversational_agent import diagnostic_agent_conversation
from ..agents.coordinator_agent import coordinator_agent
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import asyncio  # Ajoute en haut


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Google Translate
translator = Translator()

# 🗂️ État global du chatbot
class ChatState(BaseModel):
    input: str
    translated_input: str | None = None
    language: str | None = None
    answer_en: str | None = None
    output: str | None = None
    terminated: bool = False  # Flag Stop
    agent_sequence: list[str] = []  # Liste des agents choisis
    current_agent_index: int = 0    # Index du prochain agent à exécuter
    agent_done: bool = False


# 🌐 Traduction FR ➡️ EN
async def translate_to_english_node(state: ChatState) -> ChatState:
    user_input = state.input
    print("🌍 Traduction en anglais en cours...")
    result = await translator.translate(user_input, dest="en")
    print(f"✅ Traduction anglaise : {result.text} (langue détectée : {result.src})")
    state.translated_input = result.text
    state.language = result.src
    return state


# 🧠 Coordination des agents
def coordinator_node(state: ChatState) -> ChatState:
    question_en = state.translated_input or state.input
    print("🧠 [Coordinator] Analyse de la question...")
    agents_sequence = coordinator_agent(question_en)

    # Vérification de la réponse
    if not agents_sequence:
        print("⚠️ Aucun agent recommandé par le coordinator.")
        state.agent_sequence = []
        return state

    # Aplatir la séquence d'agents
    flat_agents_sequence = [agent for group in agents_sequence for agent in group]
    print(f"📋 Agents choisis : {flat_agents_sequence}")

    state.agent_sequence = flat_agents_sequence
    state.current_agent_index = 0
    return state


# # 🚀 Exécution des agents
# def agent_executor_node(state: ChatState) -> ChatState:
#     if state.current_agent_index >= len(state.agent_sequence):
#         print("✅ Tous les agents ont été exécutés.")
#         return state

#     agent_name = state.agent_sequence[state.current_agent_index]
#     question_en = state.translated_input or state.input
#     print(f"🚀 Exécution de l'agent : {agent_name}")

#     response = None
#     if agent_name == "clinical_trials":
#         response = clinical_trials_agent(question_en)
#     elif agent_name == "treatments":
#         response = treatments_agent(question_en)
#     elif agent_name == "diagnosis":
#         response, has_followup = diagnostic_agent_conversation(question_en)
#         if has_followup:
#             print("🔁 L'agent diagnosis a des questions de suivi.")
#             state.answer_en = response
#             return state  # ⚠️ Rester sur diagnosis
#     elif agent_name == "scientific_summary":
#         response = summarize_pubmed_results(query=question_en, language="en")
#     elif agent_name == "generaliste":
#         response = generaliste_agent(question_en)
#     else:
#         print(f"⚠️ Agent inconnu : {agent_name}")

#     if response:
#         print(f"✅ Réponse de {agent_name} : {response}")
#         state.answer_en = response
#     else:
#         print(f"❌ Aucun résultat de {agent_name}")

#     state.current_agent_index += 1
#     return state

async def agent_executor_node(state: ChatState) -> ChatState:
    if state.current_agent_index >= len(state.agent_sequence):
        print("✅ Tous les agents ont été exécutés.")
        return state

    agent_name = state.agent_sequence[state.current_agent_index]
    question_en = state.translated_input or state.input
    print(f"🚀 Exécution de l'agent : {agent_name}")

    response = None
    if agent_name == "clinical_trials":
        response = clinical_trials_agent(question_en)
    elif agent_name == "treatments":
        response = treatments_agent(question_en)
    elif agent_name == "diagnosis":
        response, has_followup = diagnostic_agent_conversation(question_en)
        if has_followup:
            print("🔁 L'agent diagnosis a des questions de suivi.")
            state.answer_en = response
            # ✅ Attendre la réponse de l’utilisateur
            user_followup = input("👤 Votre réponse (pour diagnostic) : ")
            state.translated_input = await translator.translate(user_followup, dest="en")
            return state  # Revenir au même agent pour continuer la conversation
    elif agent_name == "scientific_summary":
        response = summarize_pubmed_results(question_en, language="en")
    elif agent_name == "generaliste":
        response = generaliste_agent(question_en)
    else:
        print(f"⚠️ Agent inconnu : {agent_name}")

    if response:
        print(f"✅ Réponse de {agent_name} : {response}")
        state.answer_en = response
    else:
        print(f"❌ Aucun résultat de {agent_name}")

    state.current_agent_index += 1
    return state



# 🌐 Retraduction EN ➡️ Langue d’origine
async def translate_to_original_language_node(state: ChatState) -> ChatState:
    if not state.answer_en:
        print("⚠️ Pas de réponse en anglais trouvée.")
        state.output = "❌ Une erreur est survenue."
        return state

    if state.language == "en":
        state.output = state.answer_en
    else:
        result = await translator.translate(state.answer_en, dest=state.language)
        print(f"🌍 Traduction vers {state.language} : {result.text}")
        state.output = result.text
    return state


# ✅ Finalisation
def finalize_output_node(state: ChatState) -> ChatState:
    state.output = state.output or "❌ Aucune réponse générée."
    return state


# 🗺️ Construction du graphe LangGraph
workflow = StateGraph(ChatState)

# Ajout des nœuds
workflow.add_node("translate_to_english", translate_to_english_node)
workflow.add_node("coordinator", coordinator_node)
workflow.add_node("agent_executor", agent_executor_node)
workflow.add_node("translate_to_original_language", translate_to_original_language_node)
workflow.add_node("finalize_output", finalize_output_node)

# Connexions entre les nœuds
workflow.add_edge(START, "translate_to_english")
workflow.add_edge("translate_to_english", "coordinator")
workflow.add_conditional_edges(
    "coordinator",
    lambda state: "agent_executor" if state.agent_sequence else "translate_to_original_language",
    {
        "agent_executor": "agent_executor",
        "translate_to_original_language": "translate_to_original_language"
    }
)
# workflow.add_conditional_edges(
#     "agent_executor",
#     lambda state: (
#         "agent_executor" if state.current_agent_index < len(state.agent_sequence)
#         else "translate_to_original_language"
#     ),
#     {
#         "agent_executor": "agent_executor",
#         "translate_to_original_language": "translate_to_original_language"
#     }
# )
workflow.add_conditional_edges(
    "agent_executor",
    lambda state: (
        "agent_executor" if not state.terminated and state.current_agent_index < len(state.agent_sequence)
        else "translate_to_original_language"
    ),
    {
        "agent_executor": "agent_executor",
        "translate_to_original_language": "translate_to_original_language"
    }
)

workflow.add_edge("translate_to_original_language", "finalize_output")
workflow.add_edge("finalize_output", END)

# Compilation du graphe
compiled_graph = workflow.compile()


# 💬 Boucle interactive
async def run():
    print("👩‍⚕️ Chatbot médical (LangGraph + Coordinator)")
    while True:
        question = input("👤 Votre question (ou tapez 'quit' pour sortir) : ")
        if question.lower() in ["exit", "quit", "q"]:
            print("👋 À bientôt !")
            break

        result = await compiled_graph.ainvoke({"input": question})
        print(f"\n🤖 Réponse : {result['output']}\n")


if __name__ == "__main__":
    asyncio.run(run())
