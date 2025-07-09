# orchestrateur.py
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from googletrans import Translator
from ..agents.generaliste_agent import generaliste_agent
from ..agents.clinical_trials_agent import clinical_trials_agent
from ..agents.therapeutique_agent import treatments_agent
from dotenv import load_dotenv
import os
import asyncio
from pydantic import BaseModel


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Google Translate
translator = Translator()

class ChatState(BaseModel):
    input: str
    translated_input: str | None = None
    language: str | None = None
    answer_en: str | None = None
    output: str | None = None

def translate_sync(text, dest="en"):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(translator.translate(text, dest=dest))

# 🌍 Agent de traduction vers anglais
def translate_to_english_node(state: ChatState) -> ChatState:
    user_input = state.input
    print("🌍 Traduction en anglais en cours...")

    # ✅ Traduction synchrone
    result = translate_sync(user_input, dest="en")

    print(f"✅ Traduction anglaise : {result.text} (langue détectée : {result.src})")
    state.translated_input = result.text
    state.language = result.src
    return state


# 1. Fonction qui traite la question
def generaliste_node(state: ChatState) -> ChatState:
    question_en = state.translated_input or state.input
    print(f"🔍 [node] question reçue (anglais) : {question_en}")

    answer = generaliste_agent(question_en)

    print(f"✅ [node] réponse générée (anglais) : {answer}")
    state.answer_en = answer
    return state

def clinical_trials_node(state: ChatState) -> ChatState:
    question_en = state.translated_input or state.input
    print(f"🔎 [node] recherche essais cliniques pour : {question_en}")

    response = clinical_trials_agent(question_en)
    if response:
        # print(f"✅ [node] essais cliniques trouvés : {response}")
        state.answer_en = response
        # 👉 On saute le generaliste si on a trouvé une réponse
        return state
    else:
        print("➡️ [node] pas d’essais cliniques détectés, on continue")
        return state
    
def treatments_node(state: ChatState) -> ChatState:
    question_en = state.translated_input or state.input
    print(f"🔎 [node] recherche de traitements pour : {question_en}")

    response = treatments_agent(question_en)
    if response:
        # print(f"✅ [node] traitements trouvés : {response}")
        state.answer_en = response
        # 👉 On saute le generaliste si on a trouvé une réponse
        return state
    else:
        print("➡️ [node] pas de traitements trouvés, on continue")
        return state
    
# 🌍 Agent de traduction retour vers la langue d’origine
def translate_to_original_language_node(state: ChatState) -> ChatState:
    if not state.answer_en:
        print("⚠️ Pas de réponse en anglais trouvée, on utilise directement la sortie existante.")
        state.output = "❌ Une erreur est survenue."
        return state

    if state.language == "en":
        state.output = state.answer_en
        return state

    # print(f"🌍 Retraduction en {state.language} en cours...")
    result = translate_sync(state.answer_en, dest=state.language)
    # print(f"✅ Réponse retraduite : {result.text}")
    state.output = result.text
    return state

# 2. Création du graphe
workflow = StateGraph(ChatState)
# graph = StateGraph(state_schema=ChatState)


# Ajoute les nœuds
workflow.add_node("translate_to_english", translate_to_english_node)
workflow.add_node("clinical_trials", clinical_trials_node)
workflow.add_node("treatments", treatments_node)
workflow.add_node("generaliste", generaliste_node)
workflow.add_node("translate_to_original_language", translate_to_original_language_node)

# Connexions entre les nœuds
workflow.add_edge(START, "translate_to_english")
workflow.add_edge("translate_to_english", "clinical_trials")
workflow.add_conditional_edges(
    "clinical_trials",
    lambda state: "translate_to_original_language" if state.answer_en is not None else "treatments",
    {
      "translate_to_original_language": "translate_to_original_language",
      "treatments": "treatments"
    }
)
workflow.add_conditional_edges(
    "treatments",
    lambda state: "translate_to_original_language" if state.answer_en is not None else "generaliste",
    {
      "translate_to_original_language": "translate_to_original_language",
      "generaliste": "generaliste"
    }
)
# workflow.add_edge("translate_to_english", "generaliste")
workflow.add_edge("generaliste", "translate_to_original_language")
workflow.add_edge("translate_to_original_language", END)

graph = workflow.compile()

# 3. Boucle interactive
if __name__ == "__main__":
    llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=OPENAI_API_KEY)

    print("👩‍⚕️ Chatbot médical (LangGraph v0.0.54+)")
    while True:
        question = input("👤 Question : ")
        if question.lower() in ["exit", "quit", "q"]:
            print("👋 À bientôt !")
            break

        # Invocation : tu dois fournir tout le State initial, ici 'input'
        result = graph.invoke({"input": question})
        # Résultat : dictionnaire avec la clé 'output'
        print(f"🤖 Réponse : {result['output']}\n")
