from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('doctors/', views.all_doctors, name='all_doctors'),
    path('doctor/<slug:slug>/', views.doctor_single, name='doctor_single'),
    path('hospital_single/<int:id>/', views.hospital_single, name='hospital_single'),
    path('hospital_detail/', views.hospital_detail, name='hospital_detail'),
    path('searchdoc/', views.searchdoc, name='searchdoc'),
    path('searchhos/', views.searchhos, name='searchhos'),
    path('about/', views.about_us, name='about_us'),
]
