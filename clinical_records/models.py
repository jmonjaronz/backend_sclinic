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

class EmergencyAdmission(models.Model):
    class TriageLevel(models.IntegerChoices):
        LEVEL_1 = 1, 'Rojo (Inmediato)'
        LEVEL_2 = 2, 'Naranja (Muy Urgente)'
        LEVEL_3 = 3, 'Amarillo (Urgente)'
        LEVEL_4 = 4, 'Verde (Estándar)'
        LEVEL_5 = 5, 'Azul (No Urgente)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='emergencies')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    
    triage_level = models.IntegerField(choices=TriageLevel.choices)
    reason = models.TextField()
    vitals = models.JSONField(default=dict, help_text="Presión, Pulso, Temperatura, Saturación")
    
    admitted_at = models.DateTimeField(auto_now_add=True)
    specialist_in_charge = models.ForeignKey(Specialist, on_delete=models.SET_NULL, null=True, related_name='emergency_admissions')
    notes = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Emergencia: {self.patient} - Triage {self.triage_level}"

class Hospitalization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='hospitalizations')
    bed = models.ForeignKey('clinics.Bed', on_delete=models.PROTECT, related_name='hospitalizations')
    
    admission_date = models.DateTimeField(auto_now_add=True)
    expected_discharge = models.DateTimeField(null=True, blank=True)
    discharge_date = models.DateTimeField(null=True, blank=True)
    
    initial_diagnosis = models.TextField()
    final_diagnosis = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Hospitalización: {self.patient} (Cama {self.bed})"

class Treatment(models.Model):
    """
    Continuous medical treatment (medications, doses, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(ClinicalRecord, on_delete=models.CASCADE, related_name='treatments')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=255) # Ej: Tratamiento Hipertensión
    description = models.TextField()
    medications = models.JSONField(default=list, help_text="Lista de medicamentos y dosis")
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.record.patient}"
