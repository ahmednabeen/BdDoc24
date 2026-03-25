from django.contrib import admin
from .models import Doctor, Specialty, Hospital, Experience, DoctorReview, HospitalReview, ContactMessage, DoctorSubmission

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


class DoctorReviewInline(admin.TabularInline):
    model = DoctorReview 
    extra = 0
    fields = ('patient_name', 'rating', 'comment', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'hospital', 'is_featured', 'location')
    list_filter = ('hospital', 'specialties', 'is_featured',)
    search_fields = ('name', 'designation', 'specialties__name')
    readonly_fields = ('slug',)
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


@admin.register(DoctorReview) 
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient_name', 'rating', 'created_at')
    list_filter = ('doctor', 'rating', 'created_at')
    search_fields = ('doctor__name', 'patient_name', 'comment')
    readonly_fields = ('created_at',)


@admin.register(HospitalReview)
class HospitalReviewAdmin(admin.ModelAdmin):
    list_display = ('hospital', 'patient_name', 'rating', 'created_at')
    list_filter = ('hospital', 'rating', 'created_at')
    search_fields = ('hospital__name', 'patient_name', 'comment')
    readonly_fields = ('created_at',)



@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'submitted_at', 'is_read')
    list_filter = ('is_read', 'submitted_at')
    search_fields = ('first_name', 'last_name', 'email', 'message')
    readonly_fields = ('first_name', 'last_name', 'email', 'message', 'submitted_at')
    list_editable = ('is_read',) # This allows you to change the 'is_read' status directly from the list view


@admin.register(DoctorSubmission)
class DoctorSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'specialty', 'submitted_at', 'is_approved')
    list_filter = ('is_approved', 'submitted_at', 'specialty')
    search_fields = ('name', 'email', 'bmdc_registration_number')
    readonly_fields = (
        'name', 'email', 'phone_number', 'bmdc_registration_number', 
        'profile_picture', 'specialty', 'qualifications', 'location', 
        'years_of_practice', 'current_designation', 'current_workplace',
        'previous_designation', 'previous_workplace', 'submitted_at'
    )
    fieldsets = (
        ('Submission Status', {
            'fields': ('is_approved',)
        }),
        ('Submitted Information', {
            'fields': readonly_fields
        }),
    )