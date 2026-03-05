from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg
from .models import Doctor, Hospital, Specialty, Review
from django.core.paginator import Paginator
from django.db.models.functions import Coalesce

def home(request):
    # --- Data for Hero Section ---
    specialties_for_search = Specialty.objects.all().order_by('name')
    doctor_locations = Doctor.objects.values_list('location', flat=True).distinct().order_by('location')
    doctor_count = Doctor.objects.count()
    hospital_count = Hospital.objects.count()
    districts_covered = Doctor.objects.aggregate(count=Count('location', distinct=True))['count']
    review_count = Review.objects.count()

    # --- Data for Featured Doctors Section ---
    # This query now correctly handles doctors with no reviews.
    featured_doctors = Doctor.objects.filter(is_featured=True).annotate(
        review_count=Count('reviews'),
        avg_rating=Coalesce(Avg('reviews__rating'), 0.0) 
    ).order_by('-avg_rating', '-review_count')[:6]
    
    # ========================= FIX STARTS HERE =========================
    #
    # NEW, ROBUST WAY to get specialties for the filter tabs.
    # This directly queries the specialties that are linked to the featured doctors.
    #
    specialties_for_filter = Specialty.objects.filter(
        doctor__in=featured_doctors
    ).distinct().annotate(
        doc_count=Count('doctor')
    ).order_by('-doc_count')[:5]
    #
    # ========================== FIX ENDS HERE ==========================

    # --- Data for Hospitals Section ---
    hospitals = Hospital.objects.all().order_by('-id')[:4] # Showing 4 hospitals is better for a 4-column grid

    # --- Data for Browse by Specialty Section  ---
    specialties_with_counts = Specialty.objects.annotate(
        doctor_count=Count('doctor')
    ).filter(doctor_count__gt=0).order_by('-doctor_count')[:8]

    # --- Prepare the complete context ---
    context = {
        'specialties': specialties_for_search,
        'doctor_locations': doctor_locations,
        'doctor_count': doctor_count,
        'hospital_count': hospital_count,
        'districts_covered': districts_covered,
        'review_count': review_count,
        'featured_doctors': featured_doctors,
        'specialties_for_filter': specialties_for_filter, # This is now correctly populated
        'hospitals': hospitals,
        'specialties_with_counts': specialties_with_counts,
    }
    return render(request, 'myapp/index.html', context)


# NEW view for the "All Doctors" page
def all_doctors(request):
    # Annotate doctors with review data for consistent display
    doctors = Doctor.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Coalesce(Avg('reviews__rating'), 0.0)
    ).order_by('name')
    
    specialties = Specialty.objects.annotate(doctor_count=Count('doctor')).filter(doctor_count__gt=0)
    
    context = {
        'doctors': doctors,
        'specialties': specialties,
    }
    return render(request, 'myapp/doctors_detail.html', context)


def doctor_single(request, slug):
    doctor = get_object_or_404(
        Doctor.objects.select_related('hospital')
        .prefetch_related('specialties', 'experiences', 'reviews'),
        slug=slug
    )
    return render(request, 'myapp/doctors_single.html', {'doctor': doctor})


def hospital_single(request):
    return render(request, 'myapp/hospital_single.html')

def hospital_detail(request, id):
    hospital = get_object_or_404(Hospital, id=id)
    return render(request, 'myapp/hospital_detail.html', {'hospital': hospital})


def searchdoc(request):
    # Start with the same annotated queryset as the all_doctors page
    doctors = Doctor.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Coalesce(Avg('reviews__rating'), 0.0)
    )
    specialties = Specialty.objects.annotate(doctor_count=Count('doctor')).filter(doctor_count__gt=0)

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
        'doctors': doctors,
        'specialties': specialties,
    }
    return render(request, 'myapp/doctors_detail.html', context)


def searchhos(request):
    hospitals = Hospital.objects.all()

    name = request.GET.get('name')
    division = request.GET.get('division')
    district = request.GET.get('district')

    if name:
        hospitals = hospitals.filter(name__icontains=name)
    if division:
        hospitals = hospitals.filter(location__icontains=division)
    if district:
        hospitals = hospitals.filter(location__icontains=district)

    paginator = Paginator(hospitals, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'hospitals': page_obj,
    }
    return render(request, 'myapp/search_page_hos.html', context)
