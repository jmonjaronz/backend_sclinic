from django.db import models
import uuid

class Clinic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    subdomain = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Headquarters(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='headquarters')
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} - {self.clinic.name}"

class Specialty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='specialties')
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Specialties"

    def __str__(self):
        return f"{self.name} ({self.clinic.name})"

class Service(models.Model):
    class ServiceType(models.TextChoices):
        B2B = 'B2B', 'Bambú B2B'
        WELLNESS = 'WELLNESS', 'Bambú Bienestar'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='services')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255) # Ej: Consulta Psicológica
    internal_name = models.CharField(max_length=255, blank=True) # Ej: Psicoterapia
    service_type = models.CharField(max_length=20, choices=ServiceType.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField(default=60)
    is_simultaneous = models.BooleanField(default=False)
    max_capacity = models.IntegerField(default=1) # Para talleres o evaluaciones presenciales

    def __str__(self):
        return f"{self.name} - {self.clinic.name}"

class Specialist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='specialists')
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='specialist_profile')
    specialties = models.ManyToManyField(Specialty, related_name='specialists')
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.clinic.name})"
