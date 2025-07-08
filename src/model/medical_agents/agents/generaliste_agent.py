# from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv
# import os

# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# # Instanciation LLM
# llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=OPENAI_API_KEY)

# # Agent généraliste
# def generaliste_agent(query: str) -> str:
#     prompt = f"Tu es un agent généraliste en santé. Réponds simplement à la question : {query}"
#     return llm.invoke(prompt).content


# agents/generaliste_agent.py
import ollama

# Charger le modèle une seule fois
model_name = "cancer_knowlAIdge"

def generaliste_agent(user_input: str) -> str:
    """
    Fonction qui appelle le modèle Ollama pour répondre à une question.
    """
    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": user_input}]
    )
    return response['message']['content']

