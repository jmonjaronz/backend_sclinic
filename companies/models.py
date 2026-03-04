from django.db import models
from django.conf import settings
import uuid
from clinics.models import Clinic

class Company(models.Model):
    """
    Profile for a B2B company or institution.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='companies')
    ruc = models.CharField(max_length=20, unique=True)
    razon_social = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # User assigned to manage the company portal
    manager_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_company'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ruc} - {self.razon_social}"

class Agreement(models.Model):
    """
    Agreement between a Clinic and a Company.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='agreements')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='company_agreements')
    
    name = models.CharField(max_length=255, help_text="Ej: Convenio Preventivo 2024")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    benefits_description = models.TextField(blank=True)
    
    # Specific services covered (optional)
    # covered_services = models.ManyToManyField('clinics.Service', blank=True)

    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.company.razon_social} - {self.name}"

class EmployeeStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Activo'
    INACTIVE = 'INACTIVE', 'Inactivo'

class Employee(models.Model):
    """
    Link between a Patient and a Company to apply benefits.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    patient = models.OneToOneField('patients.Patient', on_delete=models.CASCADE, related_name='employment_info')
    
    job_title = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=EmployeeStatus.choices, default=EmployeeStatus.ACTIVE)
    
    hired_at = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.patient} - {self.company.razon_social}"
