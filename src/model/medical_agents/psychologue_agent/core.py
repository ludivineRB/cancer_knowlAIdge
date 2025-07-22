from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_groq import ChatGroq
from .prompts import psychologue_system_prompt
from dotenv import load_dotenv
import os

load_dotenv()

# Gestionnaire de sessions mémoire
class SimpleSessionMemoryStore:
    """Stockage en mémoire des sessions (pour le dev local)."""
    def __init__(self):
        self.sessions = {}

    def get_session_history(self, session_id: str):
        """Retourne la mémoire pour une session donnée."""
        if session_id not in self.sessions:
            self.sessions[session_id] = InMemoryChatMessageHistory()
        return self.sessions[session_id]

# Instance globale du store
memory_store = SimpleSessionMemoryStore()

def create_psychologue_agent():
    # Configure l'API Groq (clé et endpoint)
    groq_api_key = os.getenv("GROQ_API")  # stocke ta clé dans une variable d'env

    # Initialise le modèle avec Groq
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",  # ou mixtral-8x7b
        temperature=0.7,
        groq_api_key=groq_api_key
    )


    # Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", psychologue_system_prompt),
        ("human", "{input}")
    ])

    # # Mémoire conversationnelle pour garder le contexte
    # memory = ConversationBufferMemory(return_messages=True)

      # Chaîne avec gestion de l'historique
    conversation = RunnableWithMessageHistory(
        runnable=prompt | llm,
        get_session_history=memory_store.get_session_history,
        input_messages_key="input",   # Clé attendue par le prompt
        history_messages_key="history"  # Clé pour passer le contexte
    )
    print(conversation.input_schema)

    return conversation
