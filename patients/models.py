from django.db import models
from django.conf import settings
from core.models import ClinicAwareModel
import uuid


class PatientFieldConfiguration(ClinicAwareModel):
    """
    Configuración a nivel de clínica sobre qué campos del paciente son visibles u obligatorios,
    y definición de campos dinámicos extra mediante un esquema JSON.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Standard Fields Configuration (Visible / Required)
    # Ejemplo: { "address": { "visible": true, "required": false }, ... }
    standard_fields_config = models.JSONField(
        default=dict,
        help_text="Configuración de visibilidad y obligatoriedad de campos estándar."
    )

    # Custom Fields Schema
    # Ejemplo: [{"name": "allergies", "label": "Alergias", "type": "text", "required": false}]
    custom_fields_schema = models.JSONField(
        default=list,
        help_text="Esquema para campos dinámicos adicionales."
    )

    def __str__(self):
        return f"Config. Pacientes - {self.clinic.name}"


class Patient(ClinicAwareModel):
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

    class PatientStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Activo'
        INACTIVE = 'INACTIVE', 'Inactivo'
        BLOCKED = 'BLOCKED', 'Bloqueado'
        ANONYMIZED = 'ANONYMIZED', 'Anonimizado (Derecho al Olvido)'

    id = models.AutoField(primary_key=True)
    # Identificador clínico único por clínica (autoincremental por clínica)
    clinic_patient_id = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="ID único incremental del paciente dentro de su clínica (asignado al guardar)."
    )
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
    occupation = models.CharField(max_length=100, blank=True)
    religion = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True, default='Otro')
    native_language = models.CharField(max_length=100, blank=True)
    academic_degree = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    civil_status = models.CharField(max_length=50, choices=CivilStatus.choices, blank=True)

    # Estado del paciente
    status = models.CharField(
        max_length=20,
        choices=PatientStatus.choices,
        default=PatientStatus.ACTIVE,
        help_text="Estado administrativo del paciente dentro de la clínica."
    )

    # Menores / Dependientes
    is_minor = models.BooleanField(default=False)
    educational_institution = models.CharField(max_length=100, blank=True)
    grade_section = models.CharField(max_length=100, blank=True)

    # Términos y Documentos
    terms_accepted = models.BooleanField(default=False)
    dependent_doc_signed = models.FileField(upload_to='patient_docs/', null=True, blank=True)
    is_validated = models.BooleanField(default=False)  # Para dependientes
    validated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='validated_patients')
    validation_date = models.DateTimeField(null=True, blank=True)

    # Gestión Dinámica de Pacientes y Privacidad
    custom_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Valores para los campos dinámicos definidos en PatientFieldConfiguration."
    )
    is_anonymized = models.BooleanField(
        default=False,
        help_text="Derecho al olvido. Si es True, los datos identificables han sido ofuscados."
    )

    class Meta:
        unique_together = ('clinic', 'document_type', 'document_number')

    def save(self, *args, **kwargs):
        # Auto-assign clinic_patient_id if not set
        if not self.clinic_patient_id and self.clinic_id:
            last = Patient.global_objects.filter(clinic_id=self.clinic_id).order_by('-clinic_patient_id').first()
            self.clinic_patient_id = (last.clinic_patient_id or 0) + 1 if last else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.document_number})"


class PatientFamilyLink(models.Model):
    """
    Direct link between two patients (Req: 3_Pacientes.md).
    Allows family-level views and benefit inheritance.
    """
    class RelationshipType(models.TextChoices):
        PARENT = 'PARENT', 'Padre/Madre'
        CHILD = 'CHILD', 'Hijo/a'
        SPOUSE = 'SPOUSE', 'Cónyuge'
        SIBLING = 'SIBLING', 'Hermano/a'
        OTHER = 'OTHER', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_origin = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='family_links_sent')
    patient_related = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='family_links_received')
    relationship = models.CharField(max_length=20, choices=RelationshipType.choices)
    
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Activo'), ('INACTIVE', 'Inactivo')], default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient_origin', 'patient_related')

    def __str__(self):
        return f"{self.patient_origin} is {self.relationship} of {self.patient_related}"


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
    is_validated = models.BooleanField(default=False, help_text="True cuando la tutela legal ha sido verificada por la clínica.")
    document_url = models.FileField(upload_to='tutor_docs/', null=True, blank=True, help_text="Documento de autorización/tutela firmado.")
    created_at = models.DateTimeField(auto_now_add=True)


class EmergencyContact(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    relationship = models.CharField(max_length=50, blank=True)
    is_primary = models.BooleanField(default=False)


class PatientInsurance(models.Model):
    """
    Seguro o EPS asociado al paciente.
    Req: 7_0_Seguros_EPS.md sec. 8
    """
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Activo'
        INACTIVE = 'INACTIVE', 'Inactivo'
        BLOCKED = 'BLOCKED', 'Bloqueado'
        ANONYMIZED = 'ANONYMIZED', 'Anonimizado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurances')
    clinic = models.ForeignKey('core.Clinic', on_delete=models.CASCADE, related_name='patient_insurances')
    
    # Required for Req 3.3.1 (ID único por cada clinica)
    clinic_patient_id = models.PositiveIntegerField(null=True, blank=True, help_text="ID autoincremental por clínica.")
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    insurer = models.ForeignKey('insurances.Insurer', on_delete=models.CASCADE)
    plan = models.ForeignKey('insurances.InsurancePlan', on_delete=models.PROTECT)
    
    is_holder = models.BooleanField(default=True, help_text="Si es el titular del seguro.")
    holder_name = models.CharField(max_length=255, blank=True, help_text="Nombre del titular si es dependiente.")
    
    policy_number = models.CharField(max_length=100)
    affiliate_date = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.insurer.name} ({self.plan.name})"
