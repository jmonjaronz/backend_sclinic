#clinics/models_ext.py
from django.db import models
import uuid
from core.models import Clinic

class Specialty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Specialties"

class Service(models.Model):
    class ServiceType(models.TextChoices):
        B2B = 'B2B', 'Bambú B2B'
        WELLNESS = 'WELLNESS', 'Bambú Bienestar'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    name = models.CharField(max_length=255) # Ej: Consulta Psicológica
    internal_name = models.CharField(max_length=255, blank=True) # Ej: Psicoterapia
    service_type = models.CharField(max_length=20, choices=ServiceType.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField(default=60)
    is_simultaneous = models.BooleanField(default=False)
    max_capacity = models.IntegerField(default=1) # Para talleres o evaluaciones presenciales

class Specialist(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Activo'
        INACTIVE = 'INACTIVE', 'Inactivo'
        SUSPENDED = 'SUSPENDED', 'Suspendido'

    class Type(models.TextChoices):
        INTERNAL = 'INTERNAL', 'Interno'
        EXTERNAL = 'EXTERNAL', 'Externo'
        AGREEMENT = 'AGREEMENT', 'Convenio'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    
    # Identidad Desacoplada
    user = models.OneToOneField('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='specialist_profile')
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    document_type = models.CharField(max_length=20, default='DNI')
    document_number = models.CharField(max_length=50, default='')
    
    # Historial Profesional
    specialty_main = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, related_name='main_specialists')
    subspecialties = models.ManyToManyField(Specialty, related_name='sub_specialists', blank=True)
    cmp_number = models.CharField(max_length=50, blank=True, help_text="Número de Colegiatura Profesional")
    college = models.CharField(max_length=100, blank=True, default='CMP')
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    specialist_type = models.CharField(max_length=20, choices=Type.choices, default=Type.INTERNAL)
    
    bio = models.TextField(blank=True)
    
    # Logística y Vinculación
    services = models.ManyToManyField(Service, related_name='specialists', blank=True)
    headquarters = models.ManyToManyField('clinics.Headquarters', related_name='specialists', blank=True)

    class Meta:
        unique_together = ('clinic', 'document_type', 'document_number')

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or "Especialista Sin Nombre"
