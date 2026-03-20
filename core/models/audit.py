from django.db import models
from django.conf import settings
import uuid

class GlobalAuditLog(models.Model):
    """
    Registro trasversal de auditoría para acciones críticas en el sistema SaaS.
    Req: 1_Infraestructura.md sec. 4.10
    """
    class Action(models.TextChoices):
        CREATE = 'CREATE', 'Creación'
        UPDATE = 'UPDATE', 'Actualización'
        DELETE = 'DELETE', 'Eliminación'
        ACCESS = 'ACCESS', 'Acceso a datos sensibles'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Contexto
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='global_audit_logs')
    clinic = models.ForeignKey('core.Clinic', on_delete=models.CASCADE, related_name='global_audit_logs')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Acción
    action = models.CharField(max_length=20, choices=Action.choices)
    model_name = models.CharField(max_length=100, db_index=True)
    object_id = models.CharField(max_length=255, db_index=True)
    
    # Datos (Audit log inmutable)
    changes_before = models.JSONField(null=True, blank=True)
    changes_after = models.JSONField(null=True, blank=True)
    
    # Comentario adicional
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['clinic', 'model_name']),
            models.Index(fields=['clinic', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.timestamp} - {self.clinic.name} - {self.user} - {self.action} {self.model_name}"
