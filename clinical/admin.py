"""Administrative registration for normalized eye-care clinical records."""

from django.contrib import admin

from .models import (
    ClinicalExamination,
    Diagnosis,
    ExaminationDiagnosis,
    EyeFinding,
    EyeMeasurement,
    EyeglassPrescription,
    FollowUpRecommendation,
    Refraction,
    VisualAcuity,
)

admin.site.register(ClinicalExamination)
admin.site.register(Diagnosis)
admin.site.register(ExaminationDiagnosis)
admin.site.register(EyeFinding)
admin.site.register(EyeMeasurement)
admin.site.register(EyeglassPrescription)
admin.site.register(FollowUpRecommendation)
admin.site.register(Refraction)
admin.site.register(VisualAcuity)
