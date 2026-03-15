from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg
# Import DoctorReview and HospitalReview instead of the old Review
from .models import Doctor, Hospital, Specialty, DoctorReview, HospitalReview
from django.core.paginator import Paginator
from django.db.models.functions import Coalesce
import json

# This helper function now uses DoctorReview
def get_search_bar_context():
    """Helper function to get all data needed for the search bar."""
    specialties_for_search = Specialty.objects.all().order_by('name')
    doctor_locations = Doctor.objects.values_list('location', flat=True).distinct().order_by('location')
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
        
    return {
        'specialties': specialties_for_search,
        'doctor_locations': doctor_locations,
        'hospital_divisions': hospital_divisions,
        'division_district_map': division_district_map,
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
    doctors = Doctor.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Coalesce(Avg('reviews__rating'), 0.0)
    ).order_by('name')
    specialties_for_tabs = Specialty.objects.annotate(doctor_count=Count('doctor')).filter(doctor_count__gt=0)
    
    context = {
        **search_context,
        'doctors': doctors,
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

def hospital_single(request, id):
    search_context = get_search_bar_context()
    hospital = get_object_or_404(
        Hospital.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Coalesce(Avg('reviews__rating'), 0.0)
        ), 
        id=id
    )
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
    )

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
    page_obj = paginator.get_page(page_number)

    context = {
        **search_context,
        'page_obj': page_obj,
        'hospitals': page_obj,
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


def contact_us(request ):
    search_context = get_search_bar_context()
    return render(request, 'myapp/contact.html', search_context)

def privacy_policy(request):
    search_context = get_search_bar_context()
    return render(request, 'myapp/privacy_policy.html', search_context)

def terms_of_service(request):
    search_context = get_search_bar_context()
    return render(request, 'myapp/terms_of_service.html', search_context)