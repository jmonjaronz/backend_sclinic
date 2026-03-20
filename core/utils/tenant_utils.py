from clinics.models import ClinicModuleSubscription

def has_feature(clinic, feature_code):
    """
    Centraliza la lógica de verificación de módulos/funcionalidades por clínica.
    """
    if not clinic:
        return False
        
    return ClinicModuleSubscription.objects.filter(
        clinic=clinic,
        module__name=feature_code,
        module__is_active_globally=True,
        is_active=True
    ).exists()
