from django.contrib.auth.models import AbstractUser
from django.db import models
from clinics.models import Clinic

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = 'SUPERADMIN', 'SuperAdmin'
        ADMIN_CLINIC = 'ADMIN_CLINIC', 'Admin Clínica'
        PSYCHOLOGIST = 'PSYCHOLOGIST', 'Psicólogo'
        STAFF = 'STAFF', 'Personal Administrativo'
        PATIENT = 'PATIENT', 'Paciente'
        COMPANY = 'COMPANY', 'Empresa'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    document_type = models.CharField(max_length=20, blank=True, db_index=True)
    document_number = models.CharField(max_length=50, blank=True, db_index=True)

    class Meta:
        unique_together = ('clinic', 'document_type', 'document_number')

    def __str__(self):
        return f"{self.username} ({self.role})"
