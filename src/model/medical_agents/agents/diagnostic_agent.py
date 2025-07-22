from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()


client = Groq(
            api_key=os.getenv("GROQ_API")
              )
def diagnostic_agent(symptoms_en: str) -> dict:
    """
    Diagnoses potential cancer types based on symptoms using Groq LLM.
    """
    print("🩺 [agent] Diagnostic en cours avec Groq…")
    try:
        # Définir le prompt pour le LLM
        messages = [
            {"role": "system", "content": (
                "You are a medical diagnostic assistant specialized in oncology. "
                "Given a list of symptoms, suggest possible types of cancer that may be associated. "
                "Always remind the user this is not a real medical diagnosis.")},
            {"role": "user", "content": f"Symptoms: {symptoms_en}"}
        ]

        # Appel au modèle Groq
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile", # ou "llama2-70b-4096"
            max_tokens=512,
            temperature=0.3
        )

        response_text = chat_completion.choices[0].message.content
        print("✅ [agent] Diagnostic généré par Groq.")
        return {"diagnosis": response_text.strip()}

    except Exception as e:
        print(f"❌ [agent] Erreur Groq : {e}")
        return {"diagnosis": "⚠️ An error occurred while generating the diagnostic."}
