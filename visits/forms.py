from django import forms

from accounts.forms import StyledFormMixin
from accounts.models import CustomUser, StaffRole

from .models import Visit


class WalkInVisitForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Visit
        fields = ("patient", "practitioner", "chief_complaint", "notes")
        widgets = {"chief_complaint": forms.Textarea(attrs={"rows": 3}), "notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["practitioner"].queryset = CustomUser.objects.filter(role__in=[StaffRole.OPTOMETRIST, StaffRole.OPHTHALMOLOGIST], is_active=True)
