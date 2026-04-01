#core/utils/decorators.py
from functools import wraps
from rest_framework.exceptions import PermissionDenied
from core.models.tenant import get_current_clinic
from core.utils.tenant_utils import has_feature

def feature_required(feature_code):
    """
    Decorador para métodos de servicio o vistas que requieren un módulo específico.
    Utiliza el contexto global de la clínica.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            clinic = get_current_clinic()

            if not clinic:
                raise PermissionDenied("Se requiere contexto de clínica para validar esta funcionalidad.")

            if not has_feature(clinic, feature_code):
                raise PermissionDenied(f"El módulo '{feature_code}' no está habilitado para esta clínica.")

            return func(*args, **kwargs)
        return wrapper
    return decorator
