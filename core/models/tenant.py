import uuid
from django.db import models

from contextvars import ContextVar

# Context variables para almacenar la clínica y el usuario actual del request (Async safe)
_current_clinic = ContextVar("current_clinic", default=None)
_current_user = ContextVar("current_user", default=None)

def get_current_clinic():
    return _current_clinic.get()

def set_current_clinic(clinic):
    _current_clinic.set(clinic)

def get_current_user():
    return _current_user.get()

def set_current_user(user):
    _current_user.set(user)

class Clinic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    subdomain = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Activa'
        SUSPENDED = 'suspended', 'Suspendida'
        DISABLED = 'disabled', 'Deshabilitada'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )
    
    # Configuración SaaS Base
    min_booking_days_notice = models.IntegerField(default=1, help_text="Días mínimos de anticipación para agendar.")
    
    # Reglas de pago
    payment_required_before = models.BooleanField(default=True, help_text="¿Requiere pago previo para confirmar la cita?")
    payment_grace_period_days = models.IntegerField(default=1, help_text="Días antes de la cita para pagar si es requerido.")

    # Reglas de Reprogramación y Anulación
    max_reschedules_allowed = models.IntegerField(default=2, help_text="Límite de veces que se puede reprogramar una cita.")
    reschedule_notice_hours = models.IntegerField(default=24, help_text="Horas mínimas de anticipación para reprogramar.")
    cancel_notice_hours = models.IntegerField(default=24, help_text="Horas mínimas de anticipación para anular.")

    # Reglas Médicas (Se moverán o adaptarán al motor de módulos, pero se mantienen por compatibilidad inicial)
    requires_triage_before_appointment = models.BooleanField(default=False, help_text="¿Obliga a pasar por triaje antes de la consulta médica?")

    def __str__(self):
        return self.name

import logging
logger = logging.getLogger(__name__)

class ClinicGlobalManager(models.Manager):
    """
    Manager que filtra automáticamente los querysets por la clínica activa
    en el contexto (ContextVar).
    """
    def get_queryset(self):
        qs = super().get_queryset()
        clinic = get_current_clinic()
        if not clinic:
            # Falla segura: Si no hay clínica activa en el contexto, no devolvemos nada
            logger.debug(f"Acceso a {self.model.__name__} sin contexto de clínica activo.")
            return qs.none()
        return qs.filter(clinic=clinic)

    def get_global_queryset(self):
        """Método de escape para SuperAdmin/Tareas Cron"""
        return super().get_queryset()

class ClinicAwareModel(models.Model):
    """
    Clase base abstracta para modelos que pertenecen a una clínica.
    Garantiza el aislamiento multi-tenant a nivel de base de datos.
    """
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="%(class)s_objects")

    objects = ClinicGlobalManager() # Manager con aislamiento
    global_objects = models.Manager() # Manager sin aislamiento para uso interno

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['clinic', 'id']),
        ]

    def save(self, *args, **kwargs):
        # Asignación automática de la clínica si no se provee
        if not self.clinic_id:
            current = get_current_clinic()
            if current:
                self.clinic = current
            else:
                raise ValueError("Se debe especificar una clínica o tener una activa en el contexto (Multi-Tenant).")
        super().save(*args, **kwargs)
