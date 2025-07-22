from .core import create_psychologue_agent
# from langchain_core.messages import HumanMessage

def main():
    agent = create_psychologue_agent()
    session_id = "cli-session"  # identifiant unique pour la mémoire

    print("""👋 Bienvenue chez votre psychologue virtuel. Tapez 'quit' pour sortir.
Je suis ici pour vous écouter. De quoi aimeriez-vous parler aujourd’hui ?""")
    while True:
        user_input = input("Vous: ")
        if user_input.lower() in ["quit", "exit"]:
            print("👋 Merci d’avoir parlé. Prenez soin de vous.")
            break
        # Passer les inputs et le session_id
        # Envoie le message utilisateur
        response = agent.invoke(
            {"input": user_input},  # inclut la clé attendue par input_messages_key
            config={"configurable": {"session_id": session_id}}
        )

        print(f"Psy: {response.content}")

if __name__ == "__main__":
    main()
