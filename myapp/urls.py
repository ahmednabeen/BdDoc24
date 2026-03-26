from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', views.home, name='home'),
    path('doctors/', views.all_doctors, name='all_doctors'),
    path('doctor/<slug:slug>/', views.doctor_single, name='doctor_single'),
    path('hospital/<slug:slug>/', views.hospital_single, name='hospital_single'),
    path('hospital_detail/', views.hospital_detail, name='hospital_detail'),
    path('searchdoc/', views.searchdoc, name='searchdoc'),
    path('searchhos/', views.searchhos, name='searchhos'),
    path('about/', AboutUsView.as_view(), name='about_us'),
    path('contact/', views.ContactView.as_view(), name='contact_us'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('list-your-practice/', views.list_your_practice, name='list_your_practice'),
]
