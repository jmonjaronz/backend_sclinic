from django.db import models
import uuid
from django.conf import settings


class Notification(models.Model):
    """
    Notificaciones en-sistema para usuarios (no email).
    Se generan automáticamente al aprobar pagos, planes, etc.
    """
    class Type(models.TextChoices):
        APPOINTMENT_REMINDER = 'APPOINTMENT_REMINDER', 'Recordatorio de Cita'
        PAYMENT_APPROVED     = 'PAYMENT_APPROVED',     'Pago Aprobado'
        PAYMENT_REJECTED     = 'PAYMENT_REJECTED',     'Pago Rechazado'
        PLAN_APPROVED        = 'PLAN_APPROVED',         'Plan Aprobado'
        ACCOUNT_CREATED      = 'ACCOUNT_CREATED',       'Cuenta Creada'
        GENERAL              = 'GENERAL',               'General'

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    type       = models.CharField(max_length=30, choices=Type.choices, default=Type.GENERAL)
    title      = models.CharField(max_length=200)
    body       = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = '✓' if self.is_read else '●'
        return f"[{status}] {self.user} — {self.title}"
