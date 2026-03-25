from django import forms
from .models import DoctorSubmission


class ContactForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your First Name',
            'class': 'w-full pl-4 pr-4 py-3 rounded-xl bg-bg border border-border text-fg focus:outline-none focus:border-accent'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your Last Name',
            'class': 'w-full pl-4 pr-4 py-3 rounded-xl bg-bg border border-border text-fg focus:outline-none focus:border-accent'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com',
            'class': 'w-full pl-4 pr-4 py-3 rounded-xl bg-bg border border-border text-fg focus:outline-none focus:border-accent'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Write your message here...',
            'rows': 4,
            'class': 'w-full pl-4 pr-4 py-3 rounded-xl bg-bg border border-border text-fg focus:outline-none focus:border-accent'
        })
    )


class DoctorSubmissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_classes = 'w-full pl-4 pr-4 py-3 rounded-xl bg-bg border border-border text-fg focus:outline-none focus:border-accent'
        
        for field_name, field in self.fields.items():
            # Don't apply the same style to the file input field
            if field_name != 'profile_picture':
                field.widget.attrs.update({'class': tailwind_classes})
            else:
                # Add specific classes for file input if needed
                field.widget.attrs.update({'class': 'w-full text-sm text-muted file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-bccent file:text-fg hover:file:opacity-90'})

    class Meta:
        model = DoctorSubmission
        # =================== ADD NEW FIELDS TO THE LIST ===================
        fields = [
            'name', 
            'email', 
            'phone_number', 
            'bmdc_registration_number', 
            'profile_picture', # Add this
            'specialty', 
            'qualifications', 
            'location', # Add this
            'years_of_practice', # Add this
            'current_designation',
            'current_workplace',
            'previous_designation',
            'previous_workplace',
        ]
        # ==================================================================

        # =================== ADD LABELS FOR NEW FIELDS ====================
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'bmdc_registration_number': 'BMDC Registration Number',
            'profile_picture': 'Profile Picture (Optional)',
            'specialty': 'Your Primary Specialty',
            'qualifications': 'Qualifications (e.g., MBBS, FCPS)',
            'location': 'Chamber/Practice Location',
            'years_of_practice': 'Total Years of Practice',
            'current_designation': 'Current Designation',
            'current_workplace': 'Current Hospital/Chamber',
            'previous_designation': 'Previous Designation (Optional)',
            'previous_workplace': 'Previous Hospital/Chamber (Optional)',
        }