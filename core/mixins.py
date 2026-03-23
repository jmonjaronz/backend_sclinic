from rest_framework.exceptions import PermissionDenied
from core.models.tenant import get_current_clinic

class ClinicIsolationMixin:
    """
    Mixin de DRF para ViewSets que garantiza que las consultas estén restringidas
    a la clínica activa en el contexto global (ContextVar).
    """

    def get_queryset(self):
        """
        Sobrescribe get_queryset para asegurar la restricción por clínica en la API.
        Falla segura: Si no hay clínica en el contexto, retorna un queryset vacío.
        """
        assert self.queryset is not None, (
            "'%s' no definió el atributo `queryset`."
            % self.__class__.__name__
        )
        
        clinic = get_current_clinic()
        qs = super().get_queryset()

        if clinic:
            # Si el modelo hereda de ClinicAwareModel, el filtrado ya ocurre en el manager,
            # pero lo hacemos explícito para ser consistentes con modelos que no hereden de él.
            if hasattr(qs.model, 'clinic'):
                return qs.filter(clinic=clinic)
            return qs 
        
        # Falla Segura: Si no hay clínica en el contexto, no devuelve nada
        return qs.none()

    def perform_create(self, serializer):
        """
        Asigna automáticamente la clínica al crear un registro desde la API.
        """
        clinic = get_current_clinic()
        if clinic:
            serializer.save(clinic=clinic)
        else:
            raise PermissionDenied("Debe realizar la petición desde un contexto de clínica válido.")


class ClinicalAuditReadMixin:
    """
    Mixin para registrar automáticamente (audit) cuando un usuario accede (GET) a un recurso clínico sensible.
    Para que funcione correctamente, el ViewSet debe heredar este Mixin y definir `audit_resource_type`.
    Opcionalmente se puede definir el método `get_audit_patient_id(instance)`.
    """
    audit_resource_type = None

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        
        # Ejecutar la auditoría solo en respuestas exitosas
        if response.status_code == 200:
            try:
                from users.services import ClinicalAuditService
                from users.models import ClinicalAuditLog
                
                instance = self.get_object()
                patient_id = self.get_audit_patient_id(instance) if hasattr(self, 'get_audit_patient_id') else None
                resource_type = self.audit_resource_type or instance.__class__.__name__
                
                # Identificar acción por defecto o inferida
                action = ClinicalAuditLog.ActionType.VIEW_RECORD
                if resource_type == 'SessionNote':
                    action = ClinicalAuditLog.ActionType.VIEW_NOTE
                elif resource_type == 'MedicalResult':
                    action = ClinicalAuditLog.ActionType.VIEW_RESULT
                    
                ClinicalAuditService.log_action(
                    request=request,
                    action=action,
                    resource_type=resource_type,
                    resource_id=instance.pk,
                    patient_id=patient_id
                )
            except Exception as e:
                # Falla silenciosa permitida para logs de lectura, no debe interrumpir el GET principal
                # TODO: Enviar a logger (Sentry) en el futuro
                print(f"[Audit Error] Failed to log read access: {str(e)}")
                
        return response
