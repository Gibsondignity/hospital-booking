from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from clinic.models import StaffProfile
from clinic.services import next_identifier

from .models import CustomUser


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"form-control {existing}".strip()


class CustomAuthenticationForm(StyledFormMixin, AuthenticationForm):
    pass


class StaffUserCreationForm(StyledFormMixin, UserCreationForm):
    professional_title = forms.CharField(max_length=80, required=False)
    registration_number = forms.CharField(max_length=80, required=False)
    department = forms.CharField(max_length=80, required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email", "phone", "role")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("role") in {"optometrist", "ophthalmologist"} and not cleaned_data.get("registration_number"):
            self.add_error("registration_number", "Clinical practitioners need a registration number.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            StaffProfile.objects.create(
                staff_id=next_identifier(key="staff", prefix="STF"),
                user=user,
                role=user.role,
                phone=user.phone,
                professional_title=self.cleaned_data.get("professional_title", ""),
                registration_number=self.cleaned_data.get("registration_number", ""),
                department=self.cleaned_data.get("department", ""),
            )
        return user
