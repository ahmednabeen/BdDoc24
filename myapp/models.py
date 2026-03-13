from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify
from django.templatetags.static import static


class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Specialty.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class Hospital(models.Model):
    name = models.CharField(max_length=200)
    division = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    about = models.TextField(blank=True, null=True, help_text="A general description or overview of the hospital.")
    contact_numbers = models.TextField(
        blank=True, 
        null=True,
        help_text="Store multiple contact numbers separated by commas"
    )
    diagnosis = models.TextField(blank=True, null=True)
    facilities = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='records/images/', blank=True, null=True)

    def __str__(self):
        parts = [self.name]
        if self.district:
            parts.append(self.district)
        if self.division:
            parts.append(self.division)
        return ", ".join(parts)

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, null=True, blank=True)
    designation = models.CharField(max_length=100) 
    profile_picture = models.ImageField(upload_to='doctors/', null=True, blank=True)
    qualifications = models.CharField(max_length=255) 
    experience_years = models.PositiveIntegerField(null=True, blank=True)
    about = models.TextField()
    specialties = models.ManyToManyField(Specialty, blank=True)
    
    hospital = models.ForeignKey(
        Hospital, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='doctors' 
    )

    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="Unique URL-friendly identifier for the doctor.")
    is_featured = models.BooleanField(default=False)  

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            super().save(*args, **kwargs)
            self.slug = f"{slugify(self.name)}-{self.pk}"
            return super().save(update_fields=['slug'])
        return super().save(*args, **kwargs)
            
    def get_profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return static('images/default_doctor.jpg')

class Experience(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='experiences', on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=200)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.position} at {self.hospital_name}"

# =================== RENAMED THIS MODEL ===================
class DoctorReview(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='reviews', on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    rating = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.doctor.name} by {self.patient_name}"
# ==========================================================

class HospitalReview(models.Model):
    hospital = models.ForeignKey(Hospital, related_name='reviews', on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    rating = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.hospital.name} by {self.patient_name}"
