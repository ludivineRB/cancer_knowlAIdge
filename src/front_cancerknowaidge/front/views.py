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

def about(request):
    """
    About page view displaying information about the cancer care center.
    Includes mission, vision, team information, and core values.
    """
    context = {
        'page_title': 'About Us - CancerCare Medical Center',
        'meta_description': 'Learn about our mission, vision, and expert medical team dedicated to providing comprehensive cancer care with compassion and excellence.',
        'current_page': 'about'
    }
    return render(request, 'about.html', context)

def services(request):
    """
    Services page view showcasing all cancer care services.
    Displays treatment options, diagnostic services, and support programs.
    """
    context = {
        'page_title': 'Our Services - Comprehensive Cancer Care',
        'meta_description': 'Explore our comprehensive cancer care services including medical oncology, radiation therapy, surgical oncology, diagnostic services, and patient support programs.',
        'current_page': 'services'
    }
    return render(request, 'services.html', context)

def resources(request):
    """
    Resources page view providing patient and family resources.
    Includes educational materials, support groups, financial assistance, and online tools.
    """
    context = {
        'page_title': 'Patient Resources - Support & Information',
        'meta_description': 'Access comprehensive patient resources including educational materials, support groups, financial assistance, wellness programs, and online tools.',
        'current_page': 'resources'
    }
    return render(request, 'resources.html', context)

def contact(request):
    """
    Contact page view with contact information and inquiry form.
    Displays location, hours, contact methods, and contact form.
    """
    context = {
        'page_title': 'Contact Us - CancerCare Medical Center',
        'meta_description': 'Contact CancerCare Medical Center for appointments, questions, or support. Find our location, hours, phone numbers, and send us a message.',
        'current_page': 'contact'
    }
    return render(request, 'contact.html', context)