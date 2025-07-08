# graphs/medical_graph.py
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolExecutor, tools_condition
from langchain.agents import Tool
from langchain_openai import ChatOpenAI  # Si tu utilises OpenAI
from agents.generaliste_agent import generaliste_agent

# 1. Instancie le LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# 2. Définis les outils
tools = [
    Tool(
        name="Generaliste",
        func=generaliste_agent,
        description="Pour répondre aux questions de santé en vulgarisant."
    ),
]

# 3. Exécuteur de tools
executor = ToolExecutor(tools)

# 4. Définir les états
class AgentState(dict):
    pass

# 5. Graphe LangGraph
workflow = StateGraph(AgentState)
workflow.add_node("generaliste", executor)
workflow.set_entry_point("generaliste")

# Compile
app = workflow.compile()

# Test
if __name__ == "__main__":
    question = "C’est quoi le diabète et comment le prévenir ?"
    response = app.invoke({"input": question})
    print(response)
