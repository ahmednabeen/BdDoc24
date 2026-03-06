from django.contrib import admin
from .models import Doctor, Specialty, Hospital, Experience, Review


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)} 


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'division', 'district')
    search_fields = ('name', 'division', 'district')
    list_filter = ('division', 'district')

class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1
    fields = ('position', 'hospital_name', 'start_year', 'end_year', 'description')


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ('patient_name', 'rating', 'comment', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'hospital', 'is_featured', 'location')
    list_filter = ('hospital', 'specialties', 'is_featured',)
    search_fields = ('name', 'designation', 'specialties__name')
    readonly_fields = ('slug',)
    inlines = [ExperienceInline, ReviewInline]
    
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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient_name', 'rating', 'created_at')
    list_filter = ('doctor', 'rating', 'created_at')
    search_fields = ('doctor__name', 'patient_name', 'comment')
    readonly_fields = ('created_at',)

