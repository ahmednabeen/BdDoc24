from django.urls import path,include
from . import views


urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.AboutUsView.as_view(), name='about_us'),
    path('contact/', views.ContactView.as_view(), name='contact_us'),
    path('verification-policy/', views.VerificationPolicyView.as_view(), name='verification_policy'),
    path('editorial-policy/', views.EditorialPolicyView.as_view(), name='editorial_policy'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path("hospital/<slug:slug>/", views.HospitalDoctorListView.as_view(), name="hospital_detail"),
    path("doctors/<slug:department_slug>/", views.DepartmentDoctorListView.as_view(), name="department_doctors"),


    
    # Api
    path('<slug:slug>/', views.doctor_profile_view, name='doctor_profile'),
    
    
]
