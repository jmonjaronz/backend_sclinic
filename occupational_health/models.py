#occupational_health/models.py
from django.db import models
from core.models import ClinicAwareModel
from django.conf import settings
import uuid

class OccupationalEvaluation(ClinicAwareModel):
    """
    Container for an integral occupational health evaluation.
    Req: 6_2_EvaluacionOcupacional.md
    """
    class EvaluationStatus(models.TextChoices):
        INITIATED = 'INITIATED', 'Iniciada'
        IN_PROGRESS = 'IN_PROGRESS', 'En Proceso'
        PENDING_RESULTS = 'PENDING', 'Pendiente de resultados'
        OBSERVED = 'OBSERVED', 'Observada'
        COMPLETED = 'COMPLETED', 'Completada / Cerrada'
        CANCELLED = 'CANCELLED', 'Cancelada'
        EXPIRED = 'EXPIRED', 'Expirada / No finalizada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='occupational_evaluations')
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='occupational_evaluations')
    protocol = models.ForeignKey('companies.MedicalProtocol', on_delete=models.PROTECT)
    
    status = models.CharField(max_length=20, choices=EvaluationStatus.choices, default=EvaluationStatus.INITIATED)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_evaluations')

    def __str__(self):
        return f"Evaluación {self.id} - {self.patient}"

class EvaluationServiceStatus(models.Model):
    """
    Tracks the execution and results of each service within a specific evaluation.
    """
    class ServiceStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        IN_PROGRESS = 'IN_PROGRESS', 'En Proceso'
        COMPLETED = 'COMPLETED', 'Completado'
        OBSERVED = 'OBSERVED', 'Observado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluation = models.ForeignKey(OccupationalEvaluation, on_delete=models.CASCADE, related_name='service_tracking')
    protocol_service = models.ForeignKey('companies.ProtocolService', on_delete=models.PROTECT)
    
    status = models.CharField(max_length=20, choices=ServiceStatus.choices, default=ServiceStatus.PENDING)
    performer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="Especialista que realizó el examen.")
    performed_at = models.DateTimeField(null=True, blank=True)
    
    # Optional link to results (e.g., ClinicalRecord, SessionNote, or LabResult)
    # Generic relation or multiple fields could be used, for now a simple note.
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.evaluation.id} - {self.protocol_service.service.name}"

class AptitudeDictum(models.Model):
    """
    Final decision issued by the occupational doctor.
    """
    class AptitudeResult(models.TextChoices):
        APTO = 'APTO', 'Apto'
        APTO_RESTRICTED = 'APTO_RESTRICTED', 'Apto con Restricciones'
        NO_APTO = 'NO_APTO', 'No Apto'
        OBSERVED = 'OBSERVED', 'Observado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluation = models.OneToOneField(OccupationalEvaluation, on_delete=models.CASCADE, related_name='aptitude_dictum')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='aptitude_dictums')
    
    result = models.CharField(max_length=20, choices=AptitudeResult.choices)
    labor_restrictions = models.TextField(blank=True, help_text="Restricciones laborales específicas.")
    medical_recommendations = models.TextField(blank=True, help_text="Recomendaciones para el trabajador.")
    
    validity_years = models.PositiveIntegerField(default=1)
    expiry_date = models.DateField()
    
    signed_at = models.DateTimeField(auto_now_add=True)
    digital_signature_hash = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Dictamen {self.result} - {self.evaluation.patient}"
