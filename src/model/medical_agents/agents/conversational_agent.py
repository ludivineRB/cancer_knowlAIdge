from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()
# Modèle LLM via Groq
llm = ChatGroq(
    model="llama3-70b-8192",  # ou "mixtral-8x7b-32768" selon ton choix
    temperature=0,
    api_key=os.getenv("GROQ_API"),  # pense à configurer ta clé API Groq
)

# Mémoire conversationnelle pour suivre l’historique
memory = ConversationBufferMemory(return_messages=True)

# Nouveau prompt avec historique
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a medical diagnosis assistant specialized in cancer. Ask relevant questions to refine your diagnosis."),
    MessagesPlaceholder(variable_name="history"),  # correspond à la mémoire
    HumanMessage(content="{input}"),
])

# Chaîne avec mémoire
chain = prompt | llm

def diagnostic_agent_conversation(user_input: str) -> tuple[str, bool]:
    """
    Agent conversationnel qui pose des questions pour affiner son diagnostic.
    Retourne :
        - La réponse générée (str)
        - Un flag has_followup (bool) indiquant s'il reste des questions
    """
    # Ajoute le message à l’historique
    memory.save_context({"input": user_input}, {"output": ""})

    # Récupère l’historique + l’input utilisateur
    history = memory.load_memory_variables({})["history"]

    # Génère la réponse
    response = chain.invoke({
        "history": history,
        "input": user_input
    })

    # Sauvegarde la réponse dans l’historique
    memory.save_context({"input": user_input}, {"output": response.content})
    # 🔥 Détection d'une phrase clé pour savoir si l’agent continue
    if "Do you have any other symptoms?" in response.content or \
       "Can you provide more details?" in response.content:
        has_followup = True
    else:
        has_followup = False
    return response.content, has_followup
