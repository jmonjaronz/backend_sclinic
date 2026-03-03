from django.db import models
import uuid
from django.conf import settings
from clinics.models import Clinic, Headquarters, Service, Specialist
from patients.models import Patient

class Appointment(models.Model):
    class Modality(models.TextChoices):
        VIRTUAL = 'VIRTUAL', 'Virtual'
        PRESENCIAL = 'PRESENCIAL', 'Presencial'

    class Status(models.TextChoices):
        PENDING_PAYMENT = 'PENDING_PAYMENT', 'Pendiente de Pago'
        PENDING_VALIDATION = 'PENDING_VALIDATION', 'Pendiente de Validación'
        CONFIRMED = 'CONFIRMED', 'Confirmada'
        CANCELLED = 'CANCELLED', 'Cancelada'
        COMPLETED = 'COMPLETED', 'Completada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    specialist = models.ForeignKey(Specialist, on_delete=models.SET_NULL, null=True, related_name='appointments')
    headquarters = models.ForeignKey(Headquarters, on_delete=models.SET_NULL, null=True, related_name='appointments')
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    modality = models.CharField(max_length=20, choices=Modality.choices, default=Modality.PRESENCIAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT)
    
    # Payment info
    payment_voucher = models.ImageField(upload_to='vouchers/', null=True, blank=True)
    voucher_uploaded_at = models.DateTimeField(null=True, blank=True)
    validated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='validated_appointments')
    validation_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.patient} - {self.service} ({self.date} {self.start_time})"

class AvailabilityBlock(models.Model):
    """
    Blocks specific specialists or the entire clinic for certain periods.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='availability_blocks')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, null=True, blank=True, related_name='blocks') # Null means clinic-wide
    
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True) # Vacations, personal, etc.
    
    is_recurring = models.BooleanField(default=False)
    # recurring_rules = ... (could be expanded later)

    def __str__(self):
        target = self.specialist if self.specialist else "Toda la Clínica"
        return f"Bloqueo: {target} ({self.start_datetime} - {self.end_datetime})"

class TreatmentPlan(models.Model):
    """
    Groups suggested multiple sessions for a patient.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='treatment_plans')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatment_plans')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='treatment_plans')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    total_sessions = models.IntegerField(default=1)
    suggested_frequency = models.CharField(max_length=100, blank=True) # Ej: Semanal
    notes = models.TextField(blank=True)
    
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plan: {self.patient} - {self.service} ({self.total_sessions} sesiones)"
