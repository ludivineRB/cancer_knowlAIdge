# orchestrateur.py

from langgraph.graph import StateGraph, START, END
from googletrans import Translator
from ..agents.generaliste_agent import generaliste_agent
from ..agents.clinical_trials_agent import clinical_trials_agent
from ..agents.therapeutique_agent import treatments_agent
from ..agents.summarize_pubmed_agent import summarize_pubmed_results
from ..agents.conversational_agent import diagnostic_agent_conversation
from ..agents.coordinator_agent import coordinator_agent
from pydantic import BaseModel
import asyncio


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


# 🚀 Exécution des agents
def agent_executor_node(state: ChatState) -> ChatState:
    if state.current_agent_index >= len(state.agent_sequence):
        print("✅ Tous les agents ont été exécutés.")
        state.agent_done = True
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
        response = diagnostic_agent_conversation(question_en)
    elif agent_name == "generaliste":
        response = generaliste_agent(question_en)
    elif agent_name == "scientific_summary":
        response = summarize_pubmed_results(question_en, state.language or "en")
    else:
        print(f"⚠️ Agent inconnu : {agent_name}")

    # ✅ Si une réponse a été générée
    if response:
        print(f"✅ Réponse générée par {agent_name}")
        # 🛠️ Corrige ici : si c’est un tuple, on prend juste le texte
        if isinstance(response, tuple):
            response_text = response[0]
        else:
            response_text = response

        state.answer_en = response_text
        state.agent_done = True
    else:
        print(f"➡️ Aucun résultat pour l'agent {agent_name}, on passe au suivant.")
        state.current_agent_index += 1
        state.agent_done = False

    return state


# 🌍 Traduction retour EN ➡️ langue d’origine
async def translate_to_original_language_node(state: ChatState) -> ChatState:
    if not state.answer_en:
        print("⚠️ Pas de réponse en anglais trouvée, on utilise directement la sortie existante.")
        state.output = "❌ Une erreur est survenue."
        return state

    if state.language and state.language != "en":
        print(f"🌍 Retraduction en {state.language} en cours...")
        result = await translator.translate(state.answer_en, dest=state.language)
        print(f"✅ Réponse retraduite : {result.text}")
        state.output = result.text
    else:
        state.output = state.answer_en
    return state


# 🏁 Finalisation
def finalize_output_node(state: ChatState) -> ChatState:
    state.output = state.output or state.answer_en or  "❌ Aucune réponse générée."
    return state


# 🔗 Construction du graphe
workflow = StateGraph(ChatState)

# Ajoute les nœuds
workflow.add_node("translate_to_english", translate_to_english_node)
workflow.add_node("coordinator", coordinator_node)
workflow.add_node("agent_executor", agent_executor_node)
workflow.add_node("translate_to_original_language", translate_to_original_language_node)
workflow.add_node("finalize_output", finalize_output_node)

# Connexions entre les nœuds
workflow.add_edge(START, "translate_to_english")
workflow.add_edge("translate_to_english", "coordinator")
workflow.add_edge("coordinator", "agent_executor")

workflow.add_conditional_edges(
    "agent_executor",
    lambda state: (
        "translate_to_original_language"
        if state.agent_done
        else "agent_executor"
    ),
    {
        "translate_to_original_language": "translate_to_original_language",
        "agent_executor": "agent_executor",
    }
)

workflow.add_edge("translate_to_original_language", "finalize_output")
workflow.add_edge("finalize_output", END)

# Compile le graphe
compiled_graph = workflow.compile()


# 🎯 Exemple d’invocation
if __name__ == "__main__":
    print("👩‍⚕️ Chatbot médical (LangGraph)")
    while True:
        question = input("👤 Question : ")
        if question.lower() in ["exit", "quit", "q"]:
            print("👋 À bientôt !")
            break

        result = asyncio.run(compiled_graph.ainvoke({"input": question}))
        print(f"🤖 Réponse : {result['output']}\n")
