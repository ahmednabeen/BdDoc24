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
    location = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    contact_numbers = models.TextField(
        blank=True, 
        null=True,
        help_text="Store multiple contact numbers separated by commas"
    )
    diagnosis = models.TextField(blank=True, null=True)
    facilities = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='records/images/', blank=True, null=True)

    

    def __str__(self):
        return self.name

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, null=True, blank=True)
    designation = models.CharField(max_length=100) 
    profile_picture = models.ImageField(upload_to='doctors/', null=True, blank=True)
    qualifications = models.CharField(max_length=255) 
    experience_years = models.PositiveIntegerField(null=True, blank=True)
    about = models.TextField()
    specialties = models.ManyToManyField(Specialty, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="Unique URL-friendly identifier for the doctor.")
    is_featured = models.BooleanField(default=False)  


    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            super().save(*args, **kwargs)  # Get PK first
            self.slug = f"{slugify(self.name)}-{self.pk}"
            return super().save(update_fields=['slug'])
        return super().save(*args, **kwargs)
            
    def get_profile_picture_url(self):
        """Return the uploaded profile picture URL, or a default static image if none exists."""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return static('images/default_doctor.jpg')  # path in your /static/images/ folder

class Experience(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='experiences', on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=200)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True) # Can be ongoing
    description = models.TextField()

    def __str__(self):
        return f"{self.position} at {self.hospital_name}"

class Review(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='reviews', on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    rating = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.doctor.name} by {self.patient_name}"

