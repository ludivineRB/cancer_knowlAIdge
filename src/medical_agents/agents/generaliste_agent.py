from langchain_openai import ChatOpenAI

# Instanciation LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Agent généraliste
def generaliste_agent(query: str) -> str:
    prompt = f"Tu es un agent généraliste en santé. Réponds simplement à la question : {query}"
    return llm.invoke(prompt).content
