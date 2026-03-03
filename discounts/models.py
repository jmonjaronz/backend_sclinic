from django.db import models
import uuid
from clinics.models import Clinic

class B2BCompany(models.Model):
    """
    Companies with active agreements with the clinic.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    ruc = models.CharField(max_length=11, unique=True)
    is_active = models.BooleanField(default=True)
    contact_email = models.EmailField(blank=True)
    
    # Type: Educational, Industrial, etc.
    company_type = models.CharField(max_length=50, choices=[
        ('EDUCATIONAL', 'Institución Educativa'),
        ('CORPORATE', 'Corporativa'),
        ('OTHER', 'Otro'),
    ], default='CORPORATE')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CompanyAffiliation(models.Model):
    """
    Whitelist of people (employees/students) who can use the company benefits.
    """
    company = models.ForeignKey(B2BCompany, on_delete=models.CASCADE, related_name='affiliates')
    document_type = models.CharField(max_length=20, default='DNI')
    document_number = models.CharField(max_length=20)
    full_name = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ('company', 'document_type', 'document_number')

    def __str__(self):
        return f"{self.full_name} ({self.company.name})"

class Benefit(models.Model):
    """
    Definitions of discounts.
    """
    class BenefitType(models.TextChoices):
        B2B = 'B2B', 'Convenio B2B'
        FAMILY = 'FAMILY', 'Familiar'
        RECURRING = 'RECURRING', 'Cliente Frecuente'
        PROMO = 'PROMO', 'Promoción Temporal'

    name = models.CharField(max_length=255)
    benefit_type = models.CharField(max_length=20, choices=BenefitType.choices)
    
    # The higher the value, the higher the priority if multiple apply
    precedence = models.PositiveIntegerField(default=1)
    
    # Discount values
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Scoping
    company = models.ForeignKey(B2BCompany, on_delete=models.CASCADE, null=True, blank=True, related_name='benefits')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.benefit_type})"
