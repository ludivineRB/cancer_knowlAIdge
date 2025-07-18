from django.views.generic import TemplateView
from django.urls import path
from . import views
from .views import chatbot_view

urlpatterns = [
    path('', views.home, name='home'),
    path('chat', chatbot_view, name='chat'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('resources/', views.resources, name='resources'),
    path('contact/', views.contact, name='contact'),
    # Resource pages
    path('resources/treatment-guides/', views.treatment_guides, name='treatment_guides'),
    path('resources/cancer-types/', views.cancer_types, name='cancer_types'),
    path('resources/side-effect-management/', views.side_effect_management, name='side_effect_management'),
    # Detailed resource pages
    path('resources/chemotherapy-guide/', views.chemotherapy_guide, name='chemotherapy_guide'),
    path('resources/breast-cancer-info/', views.breast_cancer_info, name='breast_cancer_info'),
    path('resources/prostate-cancer-info/', views.prostate_cancer_info, name='prostate_cancer_info'),
    path('resources/lung-cancer-info/', views.lung_cancer_info, name='lung_cancer_info'),
    path('resources/skin-cancer-info/', views.skin_cancer_info, name='skin_cancer_info'),
    path('resources/colorectal-cancer-info/', views.colorectal_cancer_info, name='colorectal_cancer_info'),
    path('resources/blood-cancer-info/', views.blood_cancer_info, name='blood_cancer_info'),

    path('resources/fatigue-management/', views.fatigue_management, name='fatigue_management'),
]