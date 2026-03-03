from django.db import models
import uuid
from clinics.models import Clinic, Headquarters

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    specialties = models.ManyToManyField(Specialty)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
