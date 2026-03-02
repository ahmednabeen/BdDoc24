from django.shortcuts import render
from django.db.models import Count, Avg
from .models import Doctor, Hospital, Specialty, Review
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.

def home(request):
    # --- Data for Hero Section ---
    specialties_for_search = Specialty.objects.all().order_by('name')
    doctor_locations = Doctor.objects.values_list('location', flat=True).distinct().order_by('location')
    doctor_count = Doctor.objects.count()
    hospital_count = Hospital.objects.count()
    districts_covered = Doctor.objects.aggregate(count=Count('location', distinct=True))['count']
    review_count = Review.objects.count()

    # --- Data for Featured Doctors Section ---
    featured_doctors = Doctor.objects.filter(is_featured=True).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-avg_rating', '-review_count')[:6]
    
    featured_specialty_slugs = set()
    for doc in featured_doctors:
        for spec in doc.specialties.all():
            featured_specialty_slugs.add(spec.slug)
    
    specialties_for_filter = Specialty.objects.filter(slug__in=list(featured_specialty_slugs))[:5]

    # --- Data for Hospitals Section ---
    hospitals = Hospital.objects.all().order_by('-id')[:3]

    # --- Data for Browse by Specialty Section  ---
    specialties_with_counts = Specialty.objects.annotate(
        doctor_count=Count('doctor')
    ).filter(doctor_count__gt=0).order_by('-doctor_count')[:8]


    # --- Prepare the complete context ---
    context = {
        # Hero section context
        'specialties': specialties_for_search,
        'doctor_locations': doctor_locations,
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



def doctor_single(request):
    return render(request, 'myapp/doctors_single.html')

def doctor_detail(request, id):
    doctor = Doctor.objects.get(id=id)  # replace Doctor with your model
    return render(request, 'myapp/doctor_detail.html', {'doctor': doctor})

def hospital_single(request):
    return render(request, 'myapp/hospital_single.html')

def hospital_detail(request, id):
    hospital = Hospital.objects.get(id=id)
    return render(request, 'myapp/hospital_detail.html', {'hospital': hospital})

def searchdoc(request):
    doctors = Doctor.objects.all()

    name = request.GET.get('name')
    specialty = request.GET.get('specialty')
    location = request.GET.get('location')

    if name:
        doctors = doctors.filter(name__icontains=name)

    if specialty:
        doctors = doctors.filter(specialties__slug=specialty)

    if location:
        doctors = doctors.filter(location__icontains=location)

    doctors = doctors.distinct()

    context = {
        'doctors': doctors,
    }

    return render(request, 'myapp/search_page_doc.html', context)


# def searchhos(request):
#     hospitals = Hospital.objects.all()

#     name = request.GET.get('name')
#     division = request.GET.get('division')
#     district = request.GET.get('district')

#     if name:
#         hospitals = hospitals.filter(name__icontains=name)

#     if division:
#         hospitals = hospitals.filter(location__icontains=division)

#     if district:
#         hospitals = hospitals.filter(location__icontains=district)

#     divisions = Hospital.objects.values_list('location', flat=True).distinct()

#     context = {
#         'hospitals': hospitals,
#         'divisions': divisions,
#     }

#     return render(request, 'myapp/search_page_hos.html', context)

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

    # 🔥 Pagination
    paginator = Paginator(hospitals, 6)  # 6 hospitals per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'hospitals': page_obj,  # use page_obj in template
    }

    return render(request, 'myapp/search_page_hos.html', context)

