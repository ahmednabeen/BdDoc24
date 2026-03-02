from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('doctor/', views.doctor_single, name='doctor_single'),
    path('doctors_detail/<int:id>/', views.doctor_detail, name='doctor_detail'),
    path('hospital/', views.hospital_single, name='hospital_single'),
    path('hospital_detail/<int:id>/', views.hospital_detail, name='hospital_detail'),
    path('searchdoc/', views.searchdoc, name='searchdoc'),
    path('searchhos/', views.searchhos, name='searchhos'),
]