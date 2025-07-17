import os
import requests
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from .utils import Login
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")


def home(request):
    context = {
        'page_title': 'CancerCare - Professional Cancer Treatment & Support',
        'meta_description': 'Comprehensive cancer care services with expert treatment, compassionate support, and innovative research.',
    }
    return render(request, 'home.html', context)

@csrf_exempt  # À activer uniquement en développement
def chatbot_view(request):
    response_data = None
    if request.method == "POST":
        question = request.POST.get("question")
        language = request.POST.get("language", "fr")  # Default : français
        payload = {
            "question": question,
            "language": language
        }
        try:
            api_response = requests.post(API_URL, json=payload)
            if api_response.status_code == 200:
                response_data = api_response.json()
            else:
                response_data = {"answer": "Erreur API : " + api_response.text}
        except Exception as e:
            response_data = {"answer": f"Erreur de connexion à l'API : {str(e)}"}

    return render(request, "chatbot.html", {"response": response_data})