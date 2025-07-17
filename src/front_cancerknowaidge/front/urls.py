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
]