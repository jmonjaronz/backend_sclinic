from django.db import models
import uuid
from core.models import ClinicAwareModel
from clinics.models import Specialist
from patients.models import Patient

class ClinicalRecord(ClinicAwareModel):
    """
    Core clinical record for a patient within a specific clinic.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='clinical_record')
    assigned_specialists = models.ManyToManyField(Specialist, blank=True, related_name='assigned_records')
    
    # Datos dinámicos globales (ej. Antecedentes, Alergias)
    general_antecedents = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Datos estructurados según la plantilla de la clínica."
    )
    
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
    
    # HCE Modular: Plantilla y datos
    template = models.ForeignKey('HCETemplate', on_delete=models.SET_NULL, null=True, blank=True, help_text="Plantilla usada para esta sesión.")
    dynamic_data = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Campos llenados según la HCETemplate seleccionada."
    )
    
    # Content (Legacy or common fields)
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

class EmergencyAdmission(ClinicAwareModel):
    class TriageLevel(models.IntegerChoices):
        LEVEL_1 = 1, 'Rojo (Inmediato)'
        LEVEL_2 = 2, 'Naranja (Muy Urgente)'
        LEVEL_3 = 3, 'Amarillo (Urgente)'
        LEVEL_4 = 4, 'Verde (Estándar)'
        LEVEL_5 = 5, 'Azul (No Urgente)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='emergencies')
    
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

class VitalSigns(ClinicAwareModel):
    """
    Evolución histórica de signos vitales (Triaje).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs_history')
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='vital_signs')
    
    # Biometría
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bmi = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True) # IMC
    
    # Signos Vitales
    temperature_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    heart_rate_bpm = models.IntegerField(null=True, blank=True) # Frecuencia Cardíaca
    respiratory_rate_rpm = models.IntegerField(null=True, blank=True) # Frecuencia Respiratoria
    blood_pressure_sys = models.IntegerField(null=True, blank=True) # Sistólica
    blood_pressure_dia = models.IntegerField(null=True, blank=True) # Diastólica
    oxygen_saturation = models.IntegerField(null=True, blank=True) # SpO2 (%)
    allergy_notes = models.TextField(blank=True, help_text="Alergias reportadas durante el triaje.")
    symptoms = models.TextField(blank=True, help_text="Síntomas reportados durante el triaje.")
    observations = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    specialist = models.ForeignKey(Specialist, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """Auto-calculate IMC if height and weight are set."""
        if self.weight_kg and self.height_cm and self.height_cm > 0:
            height_m = float(self.height_cm) / 100
            self.bmi = round(float(self.weight_kg) / (height_m ** 2), 2)
        super().save(*args, **kwargs)

class PrenatalControl(models.Model):
    """
    Seguimiento de embarazo (Obstetricia).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(ClinicalRecord, on_delete=models.CASCADE, related_name='prenatal_controls')
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.CASCADE)
    
    gestational_weeks = models.IntegerField(help_text="Semanas de gestación")
    fetal_heart_rate = models.IntegerField(null=True, blank=True, help_text="Latidos fetales (LPM)")
    uterine_height_cm = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    fetal_movement = models.BooleanField(default=True)
    
    edema = models.CharField(max_length=50, blank=True)
    proteinuria = models.CharField(max_length=50, blank=True)
    
    observations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class NeonatalControl(models.Model):
    """
    Crecimiento y Desarrollo (CRED / Pediatría).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(ClinicalRecord, on_delete=models.CASCADE, related_name='neonatal_controls')
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.CASCADE)
    
    weight_grams = models.IntegerField()
    length_cm = models.DecimalField(max_digits=4, decimal_places=1)
    head_circumference_cm = models.DecimalField(max_digits=4, decimal_places=1)
    
    apgar_1min = models.IntegerField(null=True, blank=True)
    apgar_5min = models.IntegerField(null=True, blank=True)
    
    feeding_type = models.CharField(max_length=100, blank=True) # Ej: Lactancia Materna Exclusiva
    vaccines_applied = models.TextField(blank=True)
    
    neuro_development_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class HCETemplate(ClinicAwareModel):
    """
    Plantilla de Historia Clínica Electrónica Modular.
    Define qué campos se solicitarán en la Note de Sesión (SessionNote) 
    o en los antecedentes del paciente.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255) # Ej: Evolución Psicológica Adultos, Formato Ocupacional
    description = models.TextField(blank=True)
    
    # El esquema JSON define los campos (tipo, requerimiento, opciones)
    # Ej: [{"name": "motivo", "type": "textarea", "required": true}]
    schema = models.JSONField(default=list) 
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.clinic.name})"


# ---------------------------------------------------------------------------
# Medical Orders (Req: 11_HCE.md sec. 4 / 12_ResultadosClínicos.md)
# ---------------------------------------------------------------------------

class MedicalOrder(ClinicAwareModel):
    """
    Clinical order generated by a specialist from within the HCE.
    Can be for laboratory, imaging, procedures, etc.
    """
    class OrderType(models.TextChoices):
        LABORATORY = 'LAB', 'Laboratorio'
        IMAGING = 'IMAGING', 'Imágenes (Rx/Eco/TAC)'
        PROCEDURE = 'PROCEDURE', 'Procedimiento'
        SPECIALTY_REFERRAL = 'REFERRAL', 'Interconsulta'
        OTHER = 'OTHER', 'Otro'

    class Priority(models.TextChoices):
        NORMAL = 'NORMAL', 'Normal'
        URGENT = 'URGENT', 'Urgente'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_note = models.ForeignKey(SessionNote, on_delete=models.CASCADE, related_name='medical_orders')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_orders')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='orders_issued')

    order_type = models.CharField(max_length=20, choices=OrderType.choices)
    description = models.TextField(help_text="Descripción del examen o procedimiento solicitado.")
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    clinical_notes = models.TextField(blank=True, help_text="Indicaciones clínicas adicionales.")

    # Status tracking
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Orden {self.order_type} - {self.patient} ({self.created_at.date()})"


# ---------------------------------------------------------------------------
# Prescriptions (Req: 11_HCE.md sec. 4 - Recetario Digital)
# ---------------------------------------------------------------------------

class Prescription(ClinicAwareModel):
    """
    Digital prescription issued from within a session note.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_note = models.ForeignKey(SessionNote, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='prescriptions_issued')

    # Allergy override (when prescribing despite known allergy)
    allergy_override_reason = models.TextField(blank=True, help_text="Justificación médica si se prescribió a pesar de alergia detectada.")
    is_signed = models.BooleanField(default=False, help_text="True cuando el especialista ha firmado electrónicamente la receta.")
    signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receta #{self.id} - {self.patient} ({self.created_at.date()})"


class PrescriptionItem(models.Model):
    """
    Individual medication item within a prescription.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medication_name = models.CharField(max_length=255)
    concentration = models.CharField(max_length=100, blank=True, help_text="Ej: 500mg, 10mg/ml")
    dosage = models.CharField(max_length=255, help_text="Ej: 1 tableta cada 8 horas")
    route = models.CharField(max_length=100, blank=True, help_text="Ej: Oral, Intramuscular")
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    instructions = models.TextField(blank=True, help_text="Instrucciones adicionales de administración.")

    def __str__(self):
        return f"{self.medication_name} ({self.prescription.patient})"


# ---------------------------------------------------------------------------
# Referrals / Interconsultas (Req: 11_HCE.md sec. 4)
# ---------------------------------------------------------------------------

class Referral(ClinicAwareModel):
    """
    Intra-clinic referral to another specialist or service.
    """
    class ReferralStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        ACCEPTED = 'ACCEPTED', 'Aceptada'
        COMPLETED = 'COMPLETED', 'Completada'
        CANCELLED = 'CANCELLED', 'Cancelada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_note = models.ForeignKey(SessionNote, on_delete=models.SET_NULL, null=True, related_name='referrals')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='referrals')
    referring_specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='referrals_issued')
    target_specialty = models.ForeignKey('clinics.Specialty', on_delete=models.SET_NULL, null=True, blank=True)
    target_specialist = models.ForeignKey(Specialist, on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals_received')
    reason = models.TextField(help_text="Motivo de la interconsulta.")
    urgency = models.CharField(max_length=20, choices=[('ROUTINE', 'Rutinaria'), ('URGENT', 'Urgente')], default='ROUTINE')
    status = models.CharField(max_length=20, choices=ReferralStatus.choices, default=ReferralStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Interconsulta: {self.patient} -> {self.target_specialty} ({self.status})"


# ---------------------------------------------------------------------------
# Clinical Adenda (Req: 11_HCE.md sec. 6 - Nota posterior al cierre)
# ---------------------------------------------------------------------------

class ClinicalAdenda(models.Model):
    """
    Post-closure clinical note. Added after a SessionNote is locked.
    Cannot modify the original note, only annotate.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_note = models.ForeignKey(SessionNote, on_delete=models.CASCADE, related_name='adendas')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='adendas')
    content = models.TextField(help_text="Contenido de la adenda. No modifica la nota original.")
    reason = models.TextField(blank=True, help_text="Motivo de la adenda.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Adenda #{self.id} sobre nota {self.session_note.id}"


# ---------------------------------------------------------------------------
# Occupational Aptitude (Req: 11_HCE.md sec. 5 / 6_0_GestionEmpresas.md)
# ---------------------------------------------------------------------------

class OccupationalAptitude(ClinicAwareModel):
    """
    Occupational fitness result issued after an occupational protocol completion.
    The company can view the aptitude status but NOT the clinical diagnoses.
    """
    class AptitudeStatus(models.TextChoices):
        FIT = 'FIT', 'Apto'
        FIT_WITH_RESTRICTIONS = 'FIT_WITH_RESTRICTIONS', 'Apto con Restricciones'
        UNFIT = 'UNFIT', 'No Apto'
        PENDING = 'PENDING', 'Observado / Pendiente'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='occupational_aptitudes')
    session_note = models.ForeignKey(SessionNote, on_delete=models.SET_NULL, null=True, blank=True, related_name='aptitude_results')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='aptitude_results')

    # From companies module
    employee_assignment = models.OneToOneField(
        'companies.EmployeeProtocolAssignment',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='aptitude_result'
    )

    aptitude_status = models.CharField(max_length=30, choices=AptitudeStatus.choices, default=AptitudeStatus.PENDING)
    # Restrictions if FIT_WITH_RESTRICTIONS
    labor_restrictions = models.TextField(blank=True, help_text="Restricciones laborales (ej: no levantar >10kg). Solo visible para la empresa, no el diagnóstico.")

    # Internal medical notes (NOT shared with company)
    internal_notes = models.TextField(blank=True, help_text="Notas médicas internas. NO se comparten con la empresa.")

    issued_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateField(null=True, blank=True)

    # Consent to share result with company
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f"Aptitud: {self.patient} - {self.aptitude_status} ({self.issued_at.date()})"
class EvolutionNote(models.Model):
    """
    Structured evolution note following the SOAP format.
    Req: 13_Seguimiento_Pacientes_Evoluciones.md
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(ClinicalRecord, on_delete=models.CASCADE, related_name='evolutions')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='evolutions_authored')
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='evolution_note')
    
    # SOAP Structure
    subjective = models.TextField(verbose_name="S - Subjetivo", help_text="Lo que el paciente refiere.")
    objective = models.TextField(verbose_name="O - Objetivo", help_text="Hallazgos clínicos observados.")
    assessment = models.TextField(verbose_name="A - Apreciación", help_text="Interpretación clínica.")
    plan = models.TextField(verbose_name="P - Plan", help_text="Tratamiento o acciones a seguir.")
    
    # Optional flags for treatment tracking
    improvement_status = models.CharField(
        max_length=50, 
        choices=[
            ('IMPROVED', 'Mejoría clínica'),
            ('STABLE', 'Sin cambios'),
            ('WORSENED', 'Empeoramiento'),
            ('INSUFFICIENT_RESPONSE', 'Respuesta insuficiente')
        ],
        blank=True
    )
    
    is_locked = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Evolución SOAP - {self.record.patient} ({self.created_at.date()})"
