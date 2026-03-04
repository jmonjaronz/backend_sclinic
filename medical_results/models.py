from django.db import models
import uuid
from clinics.models import Clinic
from patients.models import Patient
from appointments.models import Appointment

class MedicalResult(models.Model):
    """
    General results for medical services (Laboratory, Imaging, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='medical_results')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_results')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='medical_result')
    
    class ResultType(models.TextChoices):
        LABORATORY = 'LABORATORY', 'Laboratorio'
        IMAGING = 'IMAGING', 'Imágenes / Rayos X'
        GENERAL = 'GENERAL', 'General / Otros'
    
    result_type = models.CharField(max_length=20, choices=ResultType.choices, default=ResultType.GENERAL)
    summary = models.TextField(blank=True, help_text="Resumen o conclusión del resultado")
    
    # Files
    attachment = models.FileField(upload_to='medical_results/', null=True, blank=True)
    
    performed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_result_type_display()} - {self.patient} ({self.created_at.date()})"

class LaboratoryDetail(models.Model):
    """
    Detailed numeric or text values for a lab test (e.g., Glucose: 90 mg/dL).
    """
    result = models.ForeignKey(MedicalResult, on_delete=models.CASCADE, related_name='details')
    parameter_name = models.CharField(max_length=255) # ej: "Glucosa"
    value = models.CharField(max_length=255) # ej: "90"
    unit = models.CharField(max_length=50, blank=True) # ej: "mg/dL"
    reference_range = models.CharField(max_length=255, blank=True) # ej: "70-100"
    is_abnormal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.parameter_name}: {self.value} {self.unit}"
