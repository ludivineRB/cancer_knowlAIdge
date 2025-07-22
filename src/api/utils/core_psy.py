# #
# from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.memory import ConversationBufferMemory
# from langchain_groq import ChatGroq
# from dotenv import load_dotenv
# import os

# load_dotenv()

# psychologue_system_prompt = """
# Vous êtes un psychologue virtuel empathique et bienveillant. Votre rôle est :
# - d'écouter activement l'utilisateur,
# - de reformuler ce qu'il dit pour montrer votre compréhension,
# - de poser des questions ouvertes pour l'aider à explorer ses émotions,
# - de donner des suggestions générales (pas de diagnostic médical).

# Règles :
# 1. Ne donnez jamais de conseils médicaux ou juridiques précis.
# 2. Encouragez l'utilisateur à contacter un vrai professionnel si nécessaire.
# 3. Soyez concis, doux et rassurant.
# """

# # Configure l'API Groq
# groq_api_key = os.getenv("GROQ_API")
# llm = ChatGroq(
#     model_name="llama-3.3-70b-versatile",  # ou mixtral-8x7b
#     temperature=0.7,
#     groq_api_key=groq_api_key
# )

# # Mémoire conversationnelle pour suivre l’historique
# memory = ConversationBufferMemory(
#     return_messages=True
# )

# # Nouveau prompt qui inclut l’historique
# prompt = ChatPromptTemplate.from_messages([
#     ("system", psychologue_system_prompt),
#     MessagesPlaceholder(variable_name="history"),  # 🆕 historique ici
#     ("human", "{input}")
# ])

# # Chaîne qui combine prompt + modèle + mémoire
# chain = prompt | llm

# def create_psychologue_agent():
#     """
#     Retourne une fonction qui gère la conversation
#     """
#     def agent(user_input: str):
#         # Charge l’historique et génère une réponse
#         history = memory.load_memory_variables({})["history"]
#         response = chain.invoke({
#             "history": history,
#             "input": user_input
#         })
#         # Sauvegarde le contexte (input + output)
#         memory.save_context({"input": user_input}, {"output": response.content})
#         return response.content

#     return agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langdetect import detect
from deep_translator import GoogleTranslator
import os

load_dotenv()

psychologue_system_prompt = """
Vous êtes un psychologue virtuel empathique et bienveillant. Votre rôle est :
- d'écouter activement l'utilisateur,
- de reformuler ce qu'il dit pour montrer votre compréhension,
- de poser des questions ouvertes pour l'aider à explorer ses émotions,
- de donner des suggestions générales (pas de diagnostic médical).

Règles :
1. Ne donnez jamais de conseils médicaux ou juridiques précis.
2. Encouragez l'utilisateur à contacter un vrai professionnel si nécessaire.
3. Soyez concis, doux et rassurant.
"""

# Configure l'API Groq
groq_api_key = os.getenv("GROQ_API")
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.7,
    groq_api_key=groq_api_key
)

# Mémoire conversationnelle
memory = ConversationBufferMemory(return_messages=True)

# Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", psychologue_system_prompt),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Chaîne complète
chain = prompt | llm


def translate_to_french_if_needed(text: str):
    """Détecte la langue et traduit en français si nécessaire"""
    detected_lang = detect(text)
    if detected_lang != "fr":
        translated_text = GoogleTranslator(source="auto", target="fr").translate(text)
        return translated_text, detected_lang
    return text, "fr"


def translate_back_if_needed(text: str, target_lang: str):
    """Traduit de français vers la langue originale si nécessaire"""
    if target_lang != "fr":
        return GoogleTranslator(source="fr", target=target_lang).translate(text)
    return text


def create_psychologue_agent():
    """
    Retourne une fonction qui gère la conversation
    """
    def agent(user_input: str):
        # Traduire en français si nécessaire
        translated_input, original_lang = translate_to_french_if_needed(user_input)

        # Charger l’historique et générer une réponse
        history = memory.load_memory_variables({})["history"]
        response = chain.invoke({
            "history": history,
            "input": translated_input
        })

        # Sauvegarder le contexte (input + output en français)
        memory.save_context({"input": translated_input}, {"output": response.content})

        # Retraduire la réponse si besoin
        final_response = translate_back_if_needed(response.content, original_lang)
        return final_response

    return agent
