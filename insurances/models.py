#insurances/models.py
from django.db import models
from core.models import ClinicAwareModel
import uuid

class Insurer(ClinicAwareModel):
    """
    Aseguradora con la que la clínica tiene convenio.
    Req: 7_0_Seguros_EPS.md
    """
    class InsurerType(models.TextChoices):
        EPS = 'EPS', 'EPS'
        PRIVATE = 'PRIVATE', 'Seguro Privado'
        OTHER = 'OTHER', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    insurer_type = models.CharField(max_length=20, choices=InsurerType.choices, default=InsurerType.PRIVATE)
    internal_code = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Datos de contacto
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class InsurancePlan(models.Model):
    """
    Plan específico de una aseguradora.
    """
    class NetworkType(models.TextChoices):
        OPEN = 'OPEN', 'Red Abierta'
        CLOSED = 'CLOSED', 'Red Cerrada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    insurer = models.ForeignKey(Insurer, on_delete=models.CASCADE, related_name='plans')
    name = models.CharField(max_length=255)
    network_type = models.CharField(max_length=20, choices=NetworkType.choices, default=NetworkType.CLOSED)
    requires_authorization = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.insurer.name} - {self.name}"

class InsuranceCoverage(models.Model):
    """
    Condiciones de cobertura por servicio o especialidad para un plan.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(InsurancePlan, on_delete=models.CASCADE, related_name='coverages')
    
    # Puede aplicar a un servicio específico o a toda una especialidad
    service = models.ForeignKey('clinics.Service', on_delete=models.CASCADE, null=True, blank=True)
    specialty = models.ForeignKey('clinics.Specialty', on_delete=models.CASCADE, null=True, blank=True)
    
    copay_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Monto fijo que paga el paciente.")
    coinsurance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Porcentaje que paga el paciente.")
    
    max_visits_per_year = models.PositiveIntegerField(null=True, blank=True)
    is_covered = models.BooleanField(default=True)

    def __str__(self):
        target = self.service.name if self.service else self.specialty.name
        return f"Cobertura {self.plan.name} -> {target}"
