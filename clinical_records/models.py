from django.db import models
import uuid
from clinics.models import Clinic, Specialist
from patients.models import Patient
from django.conf import settings

class ClinicalRecord(models.Model):
    """
    Core clinical record for a patient within a specific clinic.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='clinical_records')
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='clinical_record')
    assigned_specialists = models.ManyToManyField(Specialist, blank=True, related_name='assigned_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Historial: {self.patient} ({self.clinic})"

class SessionNote(models.Model):
    """
    Detailed evolution note for a specific session.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(ClinicalRecord, on_delete=models.CASCADE, related_name='session_notes')
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='session_note')
    
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='session_notes')
    date = models.DateTimeField(auto_now_add=True)
    
    # Content
    session_reason = models.TextField(verbose_name="Motivo de consulta")
    observations = models.TextField(verbose_name="Observaciones")
    diagnosis = models.TextField(blank=True, verbose_name="Diagnóstico")
    
    # Therapeutic details
    therapeutic_objective = models.TextField(blank=True, verbose_name="Objetivo terapéutico")
    recommendations = models.TextField(blank=True, verbose_name="Recomendaciones")
    commitments = models.TextField(blank=True, verbose_name="Compromisos")
    assigned_materials = models.TextField(blank=True, verbose_name="Material asignado")
    
    next_session_indications = models.TextField(blank=True, verbose_name="Indicaciones para siguiente sesión")
    
    # Control
    is_locked = models.BooleanField(default=False) # Once locked, it can't be edited (immutability)
    locked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Nota de Sesión - {self.record.patient} ({self.date.date()})"
