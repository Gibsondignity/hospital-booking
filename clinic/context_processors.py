from .models import ClinicConfiguration


def clinic_configuration(request):
    return {"clinic_configuration": ClinicConfiguration.active()}
