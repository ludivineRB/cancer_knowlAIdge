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

