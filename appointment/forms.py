from django import forms
from django.utils import timezone

from accounts.forms import StyledFormMixin
from accounts.models import CustomUser, StaffRole

from .models import Appointment


class AppointmentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ("patient", "appointment_date", "appointment_time", "practitioner", "appointment_type", "reason", "notes")
        widgets = {"appointment_date": forms.DateInput(attrs={"type": "date"}), "appointment_time": forms.TimeInput(attrs={"type": "time"}), "reason": forms.Textarea(attrs={"rows": 3}), "notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["practitioner"].queryset = CustomUser.objects.filter(role__in=[StaffRole.OPTOMETRIST, StaffRole.OPHTHALMOLOGIST], is_active=True)
        self.fields["appointment_date"].widget.attrs["min"] = timezone.localdate().isoformat()

    def clean(self):
        cleaned_data = super().clean()
        practitioner = cleaned_data.get("practitioner")
        day = cleaned_data.get("appointment_date")
        time = cleaned_data.get("appointment_time")
        if practitioner and day and time:
            existing = Appointment.objects.filter(practitioner=practitioner, appointment_date=day, appointment_time=time).exclude(status=Appointment.Status.CANCELLED).exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("The practitioner already has an appointment at this time.")
        return cleaned_data
