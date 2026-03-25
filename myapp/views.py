from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Avg
from .models import Doctor, Hospital, Specialty, DoctorReview, HospitalReview, ContactMessage
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib import messages
from .forms import ContactForm
from django.db.models.functions import Coalesce
import json  



# def get_search_bar_context():
#     """Helper function to get all data needed for the search bar."""
#     specialties_for_search = Specialty.objects.all().order_by('name')
#     doctor_locations = Doctor.objects.values_list('location', flat=True).distinct().order_by('location')
#     hospital_divisions = Hospital.objects.order_by('division').values_list('division', flat=True).distinct()
    
#     division_district_map = {}
#     all_hospitals_locations = Hospital.objects.values('division', 'district').distinct()
#     for location in all_hospitals_locations:
#         division = location['division']
#         district = location['district']
#         if division and district:
#             if division not in division_district_map:
#                 division_district_map[division] = []
#             if district not in division_district_map[division]:
#                 division_district_map[division].append(district)
#     for division in division_district_map:
#         division_district_map[division].sort()
        
#     return {
#         'specialties': specialties_for_search,
#         'doctor_locations': doctor_locations,
#         'hospital_divisions': hospital_divisions,
#         'division_district_map': division_district_map,
#     }

def get_search_bar_context():
    """
    Provides the necessary context for the search bar on every page.
    Includes data for both doctor and hospital dependent dropdowns.
    """
    # --- Data for Doctor Search ---
    specialties_for_search = Specialty.objects.all().order_by('name')
    
    # =================== NEW LOGIC FOR DOCTOR DROPDOWNS ===================
    # Create a dictionary to map each specialty (by its slug) to a list of cities
    specialty_city_map = {}
    # Get all unique combinations of doctor specialties and their locations
    doctor_locations_qs = Doctor.objects.values('specialties__slug', 'location').distinct()

    for item in doctor_locations_qs:
        specialty_slug = item['specialties__slug']
        location = item['location']
        
        # Ensure both specialty and location exist before adding them
        if specialty_slug and location:
            if specialty_slug not in specialty_city_map:
                specialty_city_map[specialty_slug] = []
            # Add the city to the list for that specialty if it's not already there
            if location not in specialty_city_map[specialty_slug]:
                specialty_city_map[specialty_slug].append(location)

    # Sort the cities within each specialty's list alphabetically
    for specialty_slug in specialty_city_map:
        specialty_city_map[specialty_slug].sort()
    # ====================================================================

    # --- Data for Hospital Search (This part remains the same) ---
    hospital_divisions = Hospital.objects.order_by('division').values_list('division', flat=True).distinct()
    division_district_map = {}
    all_hospitals_locations = Hospital.objects.values('division', 'district').distinct()
    for location in all_hospitals_locations:
        division = location['division']
        district = location['district']
        if division and district:
            if division not in division_district_map:
                division_district_map[division] = []
            if district not in division_district_map[division]:
                division_district_map[division].append(district)
    for division in division_district_map:
        division_district_map[division].sort()

    # --- Return the complete context for the search bar ---
    return {
        'specialties': specialties_for_search,
        # The old 'doctor_locations' is no longer needed for the dropdowns
        'hospital_divisions': hospital_divisions,
        'division_district_map': division_district_map,
        # Add the new map for the doctor search
        'specialty_city_map': specialty_city_map,
    }

def home(request):
    search_context = get_search_bar_context()

    doctor_count = Doctor.objects.count()
    hospital_count = Hospital.objects.count()
    districts_covered = Doctor.objects.aggregate(count=Count('location', distinct=True))['count']
    review_count = DoctorReview.objects.count() + HospitalReview.objects.count() 

    featured_doctors = Doctor.objects.filter(is_featured=True).annotate(
        review_count=Count('reviews'),
        avg_rating=Coalesce(Avg('reviews__rating'), 0.0) 
    ).order_by('-avg_rating', '-review_count')[:6]
    
    specialties_for_filter = Specialty.objects.filter(
        doctor__in=featured_doctors
    ).distinct().annotate(doc_count=Count('doctor')).order_by('-doc_count')[:5]
    
    hospitals = Hospital.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Coalesce(Avg('reviews__rating'), 0.0)
    ).order_by('-avg_rating')[:6]

    specialties_with_counts = Specialty.objects.annotate(
        doctor_count=Count('doctor')
    ).filter(doctor_count__gt=0).order_by('-doctor_count')[:8]

    context = {
        **search_context,
        'doctor_count': doctor_count,
        'hospital_count': hospital_count,
        'districts_covered': districts_covered,
        'review_count': review_count,
        'featured_doctors': featured_doctors,
        'specialties_for_filter': specialties_for_filter,
        'hospitals': hospitals,
        'specialties_with_counts': specialties_with_counts,
    }
    return render(request, 'myapp/index.html', context)



def all_doctors(request):
    search_context = get_search_bar_context()
    doctors_list = Doctor.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Coalesce(Avg('reviews__rating'), 0.0)
    ).order_by('name')
    specialties_for_tabs = Specialty.objects.annotate(doctor_count=Count('doctor')).filter(doctor_count__gt=0)
    paginator = Paginator(doctors_list, 12) 
    page_number = request.GET.get('page')
    doctors_page_obj = paginator.get_page(page_number)
    context = {
        **search_context,
        'doctors': doctors_page_obj, 
        'specialties': specialties_for_tabs,
    }
    return render(request, 'myapp/doctors_detail.html', context)


def doctor_single(request, slug):
    search_context = get_search_bar_context()
    doctor = get_object_or_404(
        Doctor.objects.select_related('hospital')
        .prefetch_related('specialties', 'experiences', 'reviews'),
        slug=slug
    )
    context = {
        **search_context,
        'doctor': doctor,
    }
    return render(request, 'myapp/doctors_single.html', context)

def hospital_detail(request):
    search_context = get_search_bar_context()
    hospitals_list = Hospital.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Coalesce(Avg('reviews__rating'), 0.0)
    ).order_by('-avg_rating')
    divisions_for_tabs = Hospital.objects.order_by('division').values_list('division', flat=True).distinct()
    paginator = Paginator(hospitals_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        **search_context,
        'hospitals': page_obj, 
        'divisions': divisions_for_tabs,
    }
    return render(request, 'myapp/hospital_detail.html', context)

def hospital_single(request, slug):
    search_context = get_search_bar_context()
    hospital = get_object_or_404(Hospital, slug=slug)
    doctors_at_hospital = Doctor.objects.filter(hospital=hospital).annotate(
        review_count=Count('reviews'),
        avg_rating=Coalesce(Avg('reviews__rating'), 0.0)
    )
    context = {
        **search_context,
        'hospital': hospital,
        'doctors': doctors_at_hospital,
    }
    return render(request, 'myapp/hospital_single.html', context)

def searchdoc(request):
    search_context = get_search_bar_context()
    doctors = Doctor.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Coalesce(Avg('reviews__rating'), 0.0)
    )
    specialties_for_tabs = Specialty.objects.annotate(doctor_count=Count('doctor')).filter(doctor_count__gt=0)

    name = request.GET.get('name')
    specialty_slug = request.GET.get('specialty')
    location = request.GET.get('location')

    if name:
        doctors = doctors.filter(name__icontains=name)
    if specialty_slug:
        doctors = doctors.filter(specialties__slug=specialty_slug)
    if location:
        doctors = doctors.filter(location__icontains=location)

    doctors = doctors.distinct()

    context = {
        **search_context,
        'doctors': doctors,
        'specialties': specialties_for_tabs,
    }
    return render(request, 'myapp/doctors_detail.html', context)

def searchhos(request):
    search_context = get_search_bar_context()
    hospitals = Hospital.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Coalesce(Avg('reviews__rating'), 0.0)
    ).order_by('name')

    name = request.GET.get('name')
    division = request.GET.get('division')
    district = request.GET.get('district')

    if name:
        hospitals = hospitals.filter(name__icontains=name)
    if division:
        hospitals = hospitals.filter(division__iexact=division)
    if district:
        hospitals = hospitals.filter(district__iexact=district)

    paginator = Paginator(hospitals, 6)
    page_number = request.GET.get('page')
    hospitals_page_obj = paginator.get_page(page_number)
    
    context = {
        **search_context,
        'hospitals': hospitals_page_obj,
    }
    return render(request, 'myapp/search_page_hos.html', context)



def about_us(request):
    search_context = get_search_bar_context()
    stats_context = {
        'doctor_count': Doctor.objects.count(),
        'hospital_count': Hospital.objects.count(),
        'districts_covered': Doctor.objects.aggregate(count=Count('location', distinct=True))['count'],
        'review_count': DoctorReview.objects.count() + HospitalReview.objects.count()
    }
    context = {**search_context, **stats_context}
    
    return render(request, 'myapp/about.html', context)


def contact_us(request):
    """
    Renders the Contact Us page and handles form submission.
    Saves the message to the database and sends an email notification.
    """
    search_context = get_search_bar_context()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        
        if form.is_valid():
            # --- Action 1: Save the message to the database ---
            ContactMessage.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message'],
            )

            # --- Action 2: Send an email notification ---
            send_mail(
                subject=f"New Contact Message from: {form.cleaned_data['first_name']} {form.cleaned_data['last_name']}",
                message=(
                    f"You have a new message from:\n"
                    f"Name: {form.cleaned_data['first_name']} {form.cleaned_data['last_name']}\n"
                    f"Email: {form.cleaned_data['email']}\n\n"
                    f"Message:\n{form.cleaned_data['message']}"
                ),
                from_email=None,  # Uses EMAIL_HOST_USER from settings.py
                recipient_list=['your.admin.email@example.com'], # IMPORTANT: Change this to your email!
                fail_silently=False, # Set to True in production if you don't want errors to stop the page
            )

            messages.success(request, "Thank you for your message! We have received it and will get back to you shortly.")
            return redirect('contact_us')
    else:
        form = ContactForm()

    context = {
        **search_context,
        'form': form,
    }
    
    return render(request, 'myapp/contact.html', context)

def privacy_policy(request):
    search_context = get_search_bar_context()
    return render(request, 'myapp/privacy_policy.html', search_context)

def terms_of_service(request):
    search_context = get_search_bar_context()
    return render(request, 'myapp/terms_of_service.html', search_context)

