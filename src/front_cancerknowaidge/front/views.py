import os
import requests
from django.shortcuts import render
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")


def home(request):
    context = {
        'page_title': 'CancerCare - Professional Cancer Treatment & Support',
        'meta_description': 'Comprehensive cancer care services with expert treatment, compassionate support, and innovative research.',
    }
    return render(request, 'home.html', context)

# @csrf_exempt  # À activer uniquement en développement
# def chatbot_view(request):
#     URL=f"{API_URL}/api/ask"
#     response_data = None
#     if request.method == "POST":
#         question = request.POST.get("question")
#         language = request.POST.get("language", "fr")  # Default : français
#         payload = {
#             "question": question,
#             "language": language
#         }
#         try:
#             api_response = requests.post(URL, json=payload)
#             if api_response.status_code == 200:
#                 response_data = api_response.json()
#             else:
#                 response_data = {"answer": "Erreur API : " + api_response.text}
#         except Exception as e:
#             response_data = {"answer": f"Erreur de connexion à l'API : {str(e)}"}

#     return render(request, "chatbot.html", {"response": response_data})


# def psychologue_view(request):
    URL=f"{API_URL}/api/psychologue"
    response_data = None
    if request.method == "POST":
        session_id = "string"
        question = request.POST.get("question")
        # language = request.POST.get("language", "fr")  # Default : français
        payload = {
            "session_id": session_id,
            "message": question
        }
        try:
            api_response = requests.post(URL, json=payload)
            if api_response.status_code == 200:
                response_data = api_response.json()
            else:
                response_data = {"answer": "Erreur API : " + api_response.text}
        except Exception as e:
            response_data = {"answer": f"Erreur de connexion à l'API : {str(e)}"}

    return render(request, "chat_psy.html", {"response": response_data})


def chat_bot_view(request):
    return render(request, "chatbot.html")

def chat_psychologue_view(request):

    return render(request, "chat_psy.html")

def about(request):
    """
    About page view displaying information about the cancer care center.
    Includes mission, vision, team information, and core values.
    """
    context = {
        'page_title': 'About Us - CancerCare Medical Center',
        'meta_description': '''Learn about our mission, vision,
                            and expert medical team dedicated to providing comprehensive
                            cancer care with compassion and excellence.''',
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
        'meta_description': '''Explore our comprehensive cancer care services including medical oncology,
                                radiation therapy, surgical oncology, diagnostic services, and patient support programs.''',
        'current_page': 'services'
    }
    return render(request, 'services.html', context)

def resources(request):
    """
    Resources page view providing patient and family resources.
    Includes educational materials, support groups, financial assistance,
    and online tools.
    """
    context = {
        'page_title': 'Patient Resources - Support & Information',
        'meta_description': '''Access comprehensive patient resources including educational materials,
                            support groups, financial assistance, wellness programs, and online tools.''',
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
        'meta_description': '''Contact CancerCare Medical Center for appointments,
                            questions, or support. Find our location, hours,
                            phone numbers, and send us a message.''',
        'current_page': 'contact'
    }
    return render(request, 'contact.html', context)

def treatment_guides(request):
    """
    Treatment guides page view with comprehensive treatment information.
    Displays detailed guides for different cancer treatment types.
    """
    context = {
        'page_title': 'Treatment Guides - Cancer Treatment Information',
        'meta_description': '''Comprehensive guides for cancer treatments including chemotherapy,
                            radiation therapy, surgery, immunotherapy, and targeted therapy.''',
        'current_page': 'treatment_guides'
    }
    return render(request, 'resources/treatment-guides.html', context)

def cancer_types(request):
    """
    Cancer types page view with information about different cancer types.
    Includes common cancers, risk factors, prevention, and warning signs.
    """
    context = {
        'page_title': 'Cancer Types - Information & Prevention',
        'meta_description': '''Learn about different types of cancer, their symptoms, risk factors,
                            prevention strategies, and warning signs to watch for.''',
        'current_page': 'cancer_types'
    }
    return render(request, 'resources/cancer-types.html', context)

def side_effect_management(request):
    """
    Side effect management page view with practical management strategies.
    Covers common side effects and coping strategies during treatment.
    """
    context = {
        'page_title': 'Side Effect Management - Treatment Support',
        'meta_description': '''Practical strategies for managing cancer treatment side effects including fatigue,
                            nausea, skin changes, and emotional support.''',
        'current_page': 'side_effect_management'
    }
    return render(request, 'resources/side-effect-management.html', context)

def chemotherapy_guide(request):
    """
    Detailed chemotherapy treatment guide.
    Comprehensive information about chemotherapy process and management.
    """
    context = {
        'page_title': 'Chemotherapy Treatment Guide - Comprehensive Information',
        'meta_description': '''Complete guide to chemotherapy treatment including how it works,
                            treatment process, side effects management, and what to expect.''',
        'current_page': 'chemotherapy_guide'
    }
    return render(request, 'resources/chemotherapy-guide.html', context)

def breast_cancer_info(request):
    """
    Comprehensive breast cancer information page.
    Covers types, screening, treatment options, and support resources.
    """
    context = {
        'page_title': 'Breast Cancer Information - Types, Screening & Treatment',
        'meta_description': ''''Comprehensive breast cancer information including types, screening guidelines,
                            treatment options, and support resources.''',
        'current_page': 'breast_cancer_info'
    }
    return render(request, 'resources/breast-cancer-info.html', context)

def prostate_cancer_info(request):
    """
    Comprehensive prostate cancer information page.
    Covers types, screening, treatment options, and support resources.
    """
    context = {
        'page_title': 'Prostate Cancer Information - Types, Screening & Treatment',
        'meta_description': '''Comprehensive prostate cancer information including types, screening guidelines,
                            treatment options, and support resources.''',
        'current_page': 'prostate_cancer_info'
    }
    return render(request, 'resources/prostate-cancer-info.html', context)

def colorectal_cancer_info(request):
    """
    Comprehensive colorectal cancer information page.
    Covers types, screening, treatment options, and support resources.
    """
    context = {
        'page_title': 'colorectal Cancer Information - Types, Screening & Treatment',
        'meta_description': '''Comprehensive colorectal cancer information including types, screening guidelines,
                            treatment options, and support resources.''',
        'current_page': 'colorectal_cancer_info'
    }
    return render(request, 'resources/colorectal-cancer-info.html', context)

def lung_cancer_info(request):
    """
    Comprehensive lung cancer information page.
    Covers types, screening, treatment options, and support resources.
    """
    context = {
        'page_title': 'Lung Cancer Information - Types, Screening & Treatment',
        'meta_description': '''Comprehensive lung cancer information including types, screening guidelines,
                            treatment options, and support resources.''',
        'current_page': 'lung_cancer_info'
    }
    return render(request, 'resources/lung-cancer-info.html', context)

def skin_cancer_info(request):
    """
    Comprehensive skin cancer information page.
    Covers types, screening, treatment options, and support resources.
    """
    context = {
        'page_title': 'skin Cancer Information - Types, Screening & Treatment',
        'meta_description': '''Comprehensive skin cancer information including types, screening guidelines,
                            treatment options, and support resources.''',
        'current_page': 'skin_cancer_info'
    }
    return render(request, 'resources/skin-cancer-info.html', context)

def blood_cancer_info(request):
    """
    Comprehensive blood cancer information page.
    Covers types, screening, treatment options, and support resources.
    """
    context = {
        'page_title': 'blood Cancer Information - Types, Screening & Treatment',
        'meta_description': '''Comprehensive blood cancer information including types, screening guidelines,
                            treatment options, and support resources.''',
        'current_page': 'blood_cancer_info'
    }
    return render(request, 'resources/blood-cancer-info.html', context)

def fatigue_management(request):
    """
    Cancer-related fatigue management strategies.
    Detailed information on understanding and managing cancer fatigue.
    """
    context = {
        'page_title': 'Cancer Fatigue Management - Strategies & Support',
        'meta_description': '''Comprehensive strategies for managing cancer-related fatigue including energy conservation,
                            exercise, sleep, and when to seek help.''',
        'current_page': 'fatigue_management'
    }
    return render(request, 'resources/fatigue-management.html', context)
