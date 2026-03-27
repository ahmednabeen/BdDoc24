from django.shortcuts import render, get_object_or_404
from .models import Specialty, Hospital, Doctor, Experience, Review
from django.core.paginator import Paginator

# new views data 
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView
from django.db.models import Avg, Count, Prefetch
from django.core.paginator import Paginator
from .models import Hospital, Doctor, Specialty



def home_view(request):
    doctor_list = Doctor.objects.all().order_by('name') # Get all doctors, ordered by name

    paginator = Paginator(doctor_list, 12) # Show 12 doctors per page
    page_number = request.GET.get('page') # Get the current page number from the URL
    page_obj = paginator.get_page(page_number) # Get the Page object for the current page

    context = {
        'page_obj': page_obj, # Pass the Page object to the template
    }
    return render(request, 'profiles/home.html', context)





def doctor_profile_view(request, slug):
    """
    Displays the detailed profile for a single doctor using their slug.
    """
    doctor = get_object_or_404(Doctor, slug=slug)
    
    # Calculate average rating and review count
    reviews = doctor.reviews.all()
    review_count = reviews.count()

    context = {
        'doctor': doctor,
        'review_count': review_count,
    }
    return render(request, 'profiles/doctor_profile.html', context)




    
# All Mew Views     

@method_decorator(cache_page(60 * 60 * 12), name='dispatch')  # cache for 12 hours
class AboutUsView(TemplateView):
    template_name = 'newapp/about.html'



@method_decorator(cache_page(60 * 60 * 12), name='dispatch') 
class ContactView(TemplateView):
    template_name = 'newapp/contact.html'
    

# @method_decorator(cache_page(60 * 60 * 12), name='dispatch')  # cache for 12 hours
class VerificationPolicyView(TemplateView):
    template_name = 'newapp/verification-policy.html'


# @method_decorator(cache_page(60 * 60 * 12), name='dispatch')  # cache for 12 hours
class EditorialPolicyView(TemplateView):
    template_name = 'newapp/editorial-policy.html'
    
    
# @method_decorator(cache_page(60 * 60 * 12), name='dispatch')  # cache for 12 hours
class PrivacyPolicyView(TemplateView):
    template_name = 'newapp/privacy.html'





class HospitalDoctorListView(DetailView):
    model = Hospital
    template_name = "newapp/hospital_doctors.html"
    context_object_name = "hospital"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Hospital.objects.prefetch_related(
            Prefetch(
                "doctors",
                queryset=Doctor.objects.select_related("hospital")
                .prefetch_related("specialties", "reviews")
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hospital = self.object

        # --- Filtering ---
        specialty_slug = self.request.GET.get("specialty")
        sort = self.request.GET.get("sort")

        doctors = hospital.doctors.all()

        # Annotate rating
        doctors = doctors.annotate(
            avg_rating=Avg("reviews__rating"),
            review_count=Count("reviews")
        )

        # Filter by specialty
        if specialty_slug:
            doctors = doctors.filter(
                specialties__slug=specialty_slug
            )

        # Sorting
        if sort == "top":
            doctors = doctors.order_by("-avg_rating")
        elif sort == "new":
            doctors = doctors.order_by("-id")

        # --- Pagination ---
        paginator = Paginator(doctors, 6)  # 6 per page (matches UI)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # --- Context ---
        context.update({
            "page_obj": page_obj,
            "doctors": page_obj.object_list,
            "specialties": Specialty.objects.all(),
            "selected_specialty": specialty_slug,
            "selected_sort": sort,
            "total_doctors": hospital.doctors.count(),
        })

        return context