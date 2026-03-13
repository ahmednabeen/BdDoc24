from django.contrib import admin
# Import DoctorReview instead of Review
from .models import Doctor, Specialty, Hospital, Experience, DoctorReview, HospitalReview

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)} 

class HospitalReviewInline(admin.TabularInline):
    model = HospitalReview
    extra = 0
    fields = ('patient_name', 'rating', 'comment', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'division', 'district')
    search_fields = ('name', 'division', 'district')
    list_filter = ('division', 'district')
    fieldsets = (
        ('Location Information', {
            'fields': ('name', 'division', 'district', 'address')
        }),
        ('Details & Facilities', {
            'fields': ('about', 'diagnosis', 'facilities', 'contact_numbers', 'image')
        }),
    )
    inlines = [HospitalReviewInline]

class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1
    fields = ('position', 'hospital_name', 'start_year', 'end_year', 'description')

# =================== RENAMED THIS CLASS ===================
class DoctorReviewInline(admin.TabularInline):
    model = DoctorReview # Use the new model name
    extra = 0
    fields = ('patient_name', 'rating', 'comment', 'created_at')
    readonly_fields = ('created_at',)
# ==========================================================

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'hospital', 'is_featured', 'location')
    list_filter = ('hospital', 'specialties', 'is_featured',)
    search_fields = ('name', 'designation', 'specialties__name')
    readonly_fields = ('slug',)
    # Use the new inline class name
    inlines = [ExperienceInline, DoctorReviewInline] 
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'designation', 'profile_picture','location',)
        }),
        ('Professional Details', {
            'fields': ('about', 'qualifications', 'experience_years', 'specialties', 'hospital',)
        }),
        ('Settings', {
            'fields': ('is_featured', 'slug',)
        }),
    )
    
    filter_horizontal = ('specialties',)

# =================== RENAMED THIS CLASS ===================
@admin.register(DoctorReview) # Use the new model name
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient_name', 'rating', 'created_at')
    list_filter = ('doctor', 'rating', 'created_at')
    search_fields = ('doctor__name', 'patient_name', 'comment')
    readonly_fields = ('created_at',)
# ==========================================================

@admin.register(HospitalReview)
class HospitalReviewAdmin(admin.ModelAdmin):
    list_display = ('hospital', 'patient_name', 'rating', 'created_at')
    list_filter = ('hospital', 'rating', 'created_at')
    search_fields = ('hospital__name', 'patient_name', 'comment')
    readonly_fields = ('created_at',)
