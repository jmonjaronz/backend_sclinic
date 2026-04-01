#users/services.py
from .models import ClinicalAuditLog

class ClinicalAuditService:
    @staticmethod
    def log_action(request, action, resource_type, resource_id, patient_id=None, before_state=None, after_state=None):
        """
        Registra una acción crítica (ej. VIEW_RECORD) en el log de auditoría clínica.
        """
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return None
            
        ip_address = request.META.get('REMOTE_ADDR')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
            
        return ClinicalAuditLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            patient_id=patient_id,
            before_state=before_state,
            after_state=after_state,
            ip_address=ip_address
        )
