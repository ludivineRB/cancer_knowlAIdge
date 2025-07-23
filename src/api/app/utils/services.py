from src.model.medical_agents.orchestrateur.orchestrateur import compiled_graph

async def process_question(question: str, language: str = "fr"):
    # Passer la question à ton graphe LangGraph
    result = await compiled_graph.ainvoke({"input": question, "language": language})

    # Adapter le résultat au format API
    return {
        "answer": result.get("output") or result.get("answer_en"),
        "articles": result.get("pubmed_links", []),
        "agents": result.get("agents", [])
    }
