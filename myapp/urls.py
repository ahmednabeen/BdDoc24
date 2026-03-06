from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    
    # URL for the "All Doctors" listing page
    path('doctors/', views.all_doctors, name='all_doctors'), 
    
    # URL for a single doctor's profile
    path('doctor/<slug:slug>/', views.doctor_single, name='doctor_single'),
    
    # Keep your hospital and search URLs as they are
    path('hospital_single/<int:id>/', views.hospital_single, name='hospital_single'),
    path('hospital_detail/', views.hospital_detail, name='hospital_detail'),
    path('searchdoc/', views.searchdoc, name='searchdoc'),
    path('searchhos/', views.searchhos, name='searchhos'),

    # The old 'doctor_detail' path has been removed.
]
