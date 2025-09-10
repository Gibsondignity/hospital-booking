from django import forms
from .models import Hospital, Doctor, Service

class HospitalForm(forms.ModelForm):
    """Form for creating and updating hospitals"""
    
    class Meta:
        model = Hospital
        fields = ['name', 'address', 'location', 'description', 'phone_number', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'address': forms.TextInput(attrs={'class': 'input'}),
            'location': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
            'phone_number': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
        }

class DoctorForm(forms.ModelForm):
    """Form for creating and updating doctors"""

    class Meta:
        model = Doctor
        fields = ['name', 'specialty', 'title', 'hospital', 'bio', 'education', 'experience_years']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'specialty': forms.TextInput(attrs={'class': 'input'}),
            'title': forms.TextInput(attrs={'class': 'input'}),
            'hospital': forms.Select(attrs={'class': 'select'}),
            'bio': forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
            'education': forms.TextInput(attrs={'class': 'input'}),
            'experience_years': forms.NumberInput(attrs={'class': 'input'}),
        }

class ServiceForm(forms.ModelForm):
    """Form for creating and updating services"""

    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'hospital', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
            'duration': forms.NumberInput(attrs={'class': 'input'}),
            'hospital': forms.Select(attrs={'class': 'select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }