from django.contrib import admin
from .models import Doctor, Specialty, Hospital, Experience, Review

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Specialty model.
    """
    list_display = ('name', 'slug')
    search_fields = ('name',)

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', )
    search_fields = ('name', 'location',)
    list_filter = ('location',)

class ExperienceInline(admin.TabularInline):
    """
    Allows editing of Experience records directly within the Doctor admin page.
    'TabularInline' provides a compact, table-based layout.
    """
    model = Experience
    extra = 1  # Provides one empty form for adding a new experience by default.
    fields = ('position', 'hospital_name', 'start_year', 'end_year', 'description')

class ReviewInline(admin.TabularInline):
    """
    Allows viewing (and adding) Review records from the Doctor admin page.
    """
    model = Review
    extra = 0  # No extra forms by default, as reviews are usually added from the frontend.
    fields = ('patient_name', 'rating', 'comment', 'created_at')
    readonly_fields = ('created_at',) # The creation date should not be editable.

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Doctor model.
    This is the main interface for managing doctors.
    """
    list_display = ('name', 'designation', 'hospital', 'experience_years', 'slug', 'is_featured', 'location')
    list_filter = ('hospital', 'specialties', 'is_featured',)
    search_fields = ('name', 'designation', 'specialties__name')
    
    # The 'slug' is auto-generated, so it should be read-only in the admin.
    # It's populated on the first save.
    readonly_fields = ('slug',)
    
    # Use inlines to manage related models directly on the doctor's page.
    inlines = [ExperienceInline, ReviewInline]
    
    # Organizes the fields into logical groups (fieldsets).
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'designation', 'profile_picture','location',)
        }),
        ('Professional Details', {
            'fields': ('about', 'qualifications', 'experience_years', 'specialties', 'hospital',)
        }),
        ('Settings', {
            'fields': ('is_featured', 'slug',) # Also good to show the readonly slug here
        }),
    )
    
    # Improves the selection interface for many-to-many fields.
    filter_horizontal = ('specialties',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Review model.
    Provides a standalone interface for managing all reviews.
    """
    list_display = ('doctor', 'patient_name', 'rating', 'created_at')
    list_filter = ('doctor', 'rating', 'created_at')
    search_fields = ('doctor__name', 'patient_name', 'comment')
    
    # Make fields that are auto-set or from the user read-only.
    readonly_fields = ('created_at',)
