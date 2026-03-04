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
        NO_SHOW = 'NO_SHOW', 'Inasistencia / Cerrado'

    class PaymentModality(models.TextChoices):
        VOUCHER = 'VOUCHER', 'Subida de Voucher (Web)'
        CASH = 'CASH', 'Efectivo / Presencial'
        TRANSFER = 'TRANSFER', 'Transferencia Directa'
        OTHER = 'OTHER', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    specialist = models.ForeignKey(Specialist, on_delete=models.SET_NULL, null=True, related_name='appointments')
    headquarters = models.ForeignKey(Headquarters, on_delete=models.SET_NULL, null=True, related_name='appointments')
    treatment_plan = models.ForeignKey('TreatmentPlan', on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    modality = models.CharField(max_length=20, choices=Modality.choices, default=Modality.PRESENCIAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT)
    payment_modality = models.CharField(max_length=20, choices=PaymentModality.choices, default=PaymentModality.VOUCHER)
    
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
    
    # Rangos de fechas para el bloqueo (Ej: Vacaciones del 10 al 20)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Para bloqueos recurrentes en un horario específico (Ej: Todos los Lunes de 9 a 11)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    # Días de la semana (0=Lunes, 6=Domingo). Almacenado como JSON o string separado por comas
    # Por simplicidad usamos CharField con validación o una lista separada por comas
    days_of_week = models.CharField(max_length=50, blank=True, help_text="0-6 separados por comas. Vacío = todos los días en el rango.")
    
    reason = models.CharField(max_length=255, blank=True) # Vacaciones, licencias, etc.
    is_recurring = models.BooleanField(default=False)
    # recurring_rules = ... (could be expanded later)

    def __str__(self):
        target = self.specialist if self.specialist else "Toda la Clínica"
        return f"Bloqueo: {target} ({self.start_date} al {self.end_date})"

class TreatmentPlan(models.Model):
    """
    Groups suggested multiple sessions for a patient.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='treatment_plans')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatment_plans')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='treatment_plans')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    specialist_creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_treatment_plans')
    
    total_sessions = models.IntegerField(default=1)
    suggested_frequency = models.CharField(max_length=100, blank=True) # Ej: Semanal
    notes = models.TextField(blank=True)
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        PARTIAL = 'PARTIAL', 'Parcial'
        PAID = 'PAID', 'Pagado'
    
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plan: {self.patient} - {self.service} ({self.total_sessions} sesiones)"
