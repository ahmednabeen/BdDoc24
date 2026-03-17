# myapp/forms.py

from django import forms

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
