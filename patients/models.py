from django.db import models
from django.conf import settings
from clinics.models import Clinic

class Patient(models.Model):
    class DocumentType(models.TextChoices):
        DNI = 'DNI', 'DNI'
        CE = 'CE', 'Carnet de Extranjería'
        PASSPORT = 'PASSPORT', 'Pasaporte'

    class CivilStatus(models.TextChoices):
        SOLTERO = 'SOLTERO', 'Soltero(a)'
        CASADO = 'CASADO', 'Casado(a)'
        VIUDO = 'VIUDO', 'Viudo(a)'
        DIVORCIADO = 'DIVORCIADO', 'Divorciado(a)'

    class Gender(models.TextChoices):
        MALE = 'MALE', 'Masculino'
        FEMALE = 'FEMALE', 'Femenino'
        OTHER = 'OTHER', 'Otro'

    id = models.AutoField(primary_key=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='patients')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='patient_profile')
    
    # Datos básicos
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    document_type = models.CharField(max_length=20, choices=DocumentType.choices, default=DocumentType.DNI)
    document_number = models.CharField(max_length=50)
    birth_date = models.DateField()
    gender = models.CharField(max_length=20, choices=Gender.choices, blank=True)
    
    # Ubicación
    department = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    
    # Otros datos
    occupation = models.CharField(max_length=100, blank=True) # Cargo
    religion = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True, default='Otro')
    native_language = models.CharField(max_length=100, blank=True) # Idioma materno
    academic_degree = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    civil_status = models.CharField(max_length=50, choices=CivilStatus.choices, blank=True)
    
    # Menores / Dependientes
    is_minor = models.BooleanField(default=False)
    educational_institution = models.CharField(max_length=100, blank=True)
    grade_section = models.CharField(max_length=100, blank=True)
    
    # Términos y Documentos
    terms_accepted = models.BooleanField(default=False)
    dependent_doc_signed = models.FileField(upload_to='patient_docs/', null=True, blank=True)
    is_validated = models.BooleanField(default=False) # Para dependientes

    class Meta:
        unique_together = ('clinic', 'document_type', 'document_number')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.document_number})"

class DependentLink(models.Model):
    class Relationship(models.TextChoices):
        PADRE = 'PADRE', 'Padre'
        MADRE = 'MADRE', 'Madre'
        TUTOR = 'TUTOR', 'Tutor Legal'
        HIJO = 'HIJO', 'Hijo(a)'
        CONYUGE = 'CONYUGE', 'Cónyuge'
        OTRO = 'OTRO', 'Otro'

    id = models.AutoField(primary_key=True)
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dependent_links')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='tutor_links')
    relationship = models.CharField(max_length=50, choices=Relationship.choices)
    created_at = models.DateTimeField(auto_now_add=True)

class EmergencyContact(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    relationship = models.CharField(max_length=50, blank=True)
