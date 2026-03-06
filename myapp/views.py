from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg
from .models import Doctor, Hospital, Specialty, Review
from django.core.paginator import Paginator
from django.db.models.functions import Coalesce

def home(request):
    # --- Data for Hero Section (Doctor Search) ---
    specialties_for_search = Specialty.objects.all().order_by('name')
    doctor_locations = Doctor.objects.values_list('location', flat=True).distinct().order_by('location')
    
    # --- Data for Hero Section (Hospital Search) ---
    hospital_divisions = Hospital.objects.order_by('division').values_list('division', flat=True).distinct()
    hospital_districts = Hospital.objects.order_by('district').values_list('district', flat=True).distinct()

    # --- Data for Quick Stats ---
    doctor_count = Doctor.objects.count()
    hospital_count = Hospital.objects.count()
    districts_covered = Doctor.objects.aggregate(count=Count('location', distinct=True))['count']
    review_count = Review.objects.count()

    # --- Data for Featured Doctors Section ---
    featured_doctors = Doctor.objects.filter(is_featured=True).annotate(
        review_count=Count('reviews'),
        avg_rating=Coalesce(Avg('reviews__rating'), 0.0) 
    ).order_by('-avg_rating', '-review_count')[:6]
    
    # --- Data for Featured Doctors' Specialty Filter Tabs ---
    specialties_for_filter = Specialty.objects.filter(
        doctor__in=featured_doctors
    ).distinct().annotate(
        doc_count=Count('doctor')
    ).order_by('-doc_count')[:5]

    # --- Data for Hospitals Section ---
    hospitals = Hospital.objects.all().order_by('-id')[:4]

    # --- Data for Browse by Specialty Section ---
    specialties_with_counts = Specialty.objects.annotate(
        doctor_count=Count('doctor')
    ).filter(doctor_count__gt=0).order_by('-doctor_count')[:8]

    # --- Prepare the complete context ---
    context = {
        # Hero section context
        'specialties': specialties_for_search,
        'doctor_locations': doctor_locations,
        'hospital_divisions': hospital_divisions,
        'hospital_districts': hospital_districts,

        # Quick Stats context
        'doctor_count': doctor_count,
        'hospital_count': hospital_count,
        'districts_covered': districts_covered,
        'review_count': review_count,

        # Featured Doctors context
        'featured_doctors': featured_doctors,
        'specialties_for_filter': specialties_for_filter,
        
        # Hospitals context
        'hospitals': hospitals,

        # Specialties context 
        'specialties_with_counts': specialties_with_counts,
    }
    return render(request, 'myapp/index.html', context)


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


def hospital_detail(request): # The 'id' parameter is removed
    hospitals_list = Hospital.objects.all().order_by('name')
    divisions = Hospital.objects.order_by('division').values_list('division', flat=True).distinct()
    paginator = Paginator(hospitals_list, 9) # Show 9 hospitals per page (for a 3-column grid)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'hospitals': page_obj, 
        'divisions': divisions,
    }
    return render(request, 'myapp/hospital_detail.html', context)




def hospital_single(request, id):
    # Get the specific hospital object, or return a 404 error if not found
    hospital = get_object_or_404(Hospital, id=id)
    
    # Find all doctors who are linked to this hospital.
    # Also, pre-calculate their review counts and average ratings for display.
    doctors_at_hospital = Doctor.objects.filter(hospital=hospital).annotate(
        review_count=Count('reviews'),
        avg_rating=Coalesce(Avg('reviews__rating'), 0.0)
    )

    context = {
        'hospital': hospital,
        'doctors': doctors_at_hospital, # Pass the list of doctors to the template
    }
    return render(request, 'myapp/hospital_single.html', context)




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

    # Use the new 'division' field for filtering
    if division:
        hospitals = hospitals.filter(division__iexact=division)

    # Use the new 'district' field for filtering
    if district:
        hospitals = hospitals.filter(district__iexact=district)

    paginator = Paginator(hospitals, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'hospitals': page_obj,
    }
    return render(request, 'myapp/search_page_hos.html', context)
