import uuid
from django.db import models

import threading

# Thread-local storage para almacenar la clínica actual del request
_thread_locals = threading.local()

def get_current_clinic():
    return getattr(_thread_locals, 'clinic', None)

def set_current_clinic(clinic):
    _thread_locals.clinic = clinic

class Clinic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    subdomain = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
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

class ClinicGlobalManager(models.Manager):
    """
    Manager que filtra automáticamente los querysets por la clínica activa
    en el thread local.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        clinic = get_current_clinic()
        if clinic:
            return qs.filter(clinic=clinic)
        return qs

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

    def save(self, *args, **kwargs):
        # Asignación automática de la clínica si no se provee
        if not self.clinic_id:
            current = get_current_clinic()
            if current:
                self.clinic = current
            else:
                raise ValueError("Se debe especificar una clínica o tener una activa en el contexto (Multi-Tenant).")
        super().save(*args, **kwargs)
