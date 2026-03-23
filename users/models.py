from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from core.models import Clinic
import uuid


class User(AbstractUser):
    """Base user identity. Role is legacy for quick access; dynamic roles via UserRole."""
    class Role(models.TextChoices):
        SUPERADMIN = 'SUPERADMIN', 'SuperAdmin'
        ADMIN_CLINIC = 'ADMIN_CLINIC', 'Admin Clínica'
        SPECIALIST = 'SPECIALIST', 'Especialista'
        STAFF = 'STAFF', 'Personal Administrativo'
        PATIENT = 'PATIENT', 'Paciente'
        COMPANY = 'COMPANY', 'Empresa'

    class PortalType(models.TextChoices):
        INTRANET = 'INTRANET', 'Portal Intranet (Staff/Clínica)'
        PATIENT = 'PATIENT', 'Portal Paciente'
        B2B = 'B2B', 'Portal Empresarial (B2B)'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    active_role = models.ForeignKey('DynamicRole', on_delete=models.SET_NULL, null=True, blank=True, related_name='active_users')
    
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    document_type = models.CharField(max_length=20, blank=True, db_index=True)
    document_number = models.CharField(max_length=50, blank=True, db_index=True)

    class Meta:
        unique_together = ('clinic', 'document_type', 'document_number')

    def __str__(self):
        return f"{self.username} ({self.role})"

    def switch_active_role(self, dynamic_role):
        """
        Req: 2_Usuarios_Permisos.md sec. 2 - Asignación de Roles
        Allows selecting the active role during the session.
        """
        if dynamic_role in self.dynamic_roles.all():
            self.active_role = dynamic_role
            self.save()
            return True
        return False

    def has_permission(self, permission_codename):
        """
        Verifica si el rol activo del usuario cuenta con el Capability específico.
        Formato esperado: <modulo>.<recurso>.<accion> (ej: patient.record.read)
        """
        # SuperAdmins tienen acceso total por defecto
        if self.role == self.Role.SUPERADMIN:
            return True
        
        # Debe tener un rol activo seleccionado
        if getattr(self, 'active_role', None) and self.active_role.is_active:
            return self.active_role.capabilities.filter(codename=permission_codename).exists()
            
        return False


# ---------------------------------------------------------------------------
# 2. Sistema de Roles Dinámicos (requerimiento 2_Usuarios_Permisos.md)
# ---------------------------------------------------------------------------

class Capability(models.Model):
    """
    Granular permission (capability) that can be assigned to roles.
    E.g. 'view_clinical_record', 'edit_appointment', 'approve_prescription'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codename = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    module = models.CharField(max_length=100, blank=True, help_text="Módulo al que pertenece, ej: clinical_records")

    def __str__(self):
        return self.codename


class RoleTemplate(models.Model):
    """
    Plantillas base globales del sistema (ej: ROLE_TEMPLATE_DOCTOR).
    Las clínicas clonan estas plantillas para crear sus propios DynamicRoles.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="Ej: ROLE_TEMPLATE_DOCTOR")
    description = models.TextField(blank=True)
    capabilities = models.ManyToManyField(Capability, blank=True, related_name='templates')
    
    def __str__(self):
        return self.name


class DynamicRole(models.Model):
    """
    Clinic-specific role defined in the database.
    Allows each clinic to create its own roles (e.g. 'Psicólogo Tratante').
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='dynamic_roles')
    name = models.CharField(max_length=100)
    capabilities = models.ManyToManyField(Capability, blank=True, related_name='roles')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('clinic', 'name')

    def clean(self):
        """Req: 2_Usuarios_Permisos.md sec 2.3 - Un rol debe tener al menos un permiso."""
        if self.pk and not self.capabilities.exists():
            raise ValidationError("El rol debe tener al menos un permiso asignado.")

    def __str__(self):
        return f"{self.name} ({self.clinic.name})"


class UserRole(models.Model):
    """Assigns a DynamicRole to a User within a clinic. A user can have multiple roles."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dynamic_roles')
    role = models.ForeignKey(DynamicRole, on_delete=models.CASCADE, related_name='user_assignments')
    is_primary = models.BooleanField(default=False, help_text="Rol activo por defecto al iniciar sesión")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.username} -> {self.role.name}"


# ---------------------------------------------------------------------------
# 3. Auditoría de Acceso Clínico (requerimiento 2_Usuarios_Permisos.md)
# ---------------------------------------------------------------------------

class ClinicalAuditLog(models.Model):
    """
    Mandatory read-audit record for sensitive clinical events.
    Triggered whenever a user opens a clinical record, note, or result.
    """
    class ActionType(models.TextChoices):
        VIEW_RECORD = 'VIEW_RECORD', 'Ver Historia Clínica'
        VIEW_NOTE = 'VIEW_NOTE', 'Ver Nota de Sesión'
        VIEW_RESULT = 'VIEW_RESULT', 'Ver Resultado Clínico'
        DOWNLOAD_DOC = 'DOWNLOAD_DOC', 'Descargar Documento'
        EDIT_RECORD = 'EDIT_RECORD', 'Editar Registro'
        SIGN_RECORD = 'SIGN_RECORD', 'Firmar Registro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    active_role = models.ForeignKey(DynamicRole, on_delete=models.SET_NULL, null=True, blank=True)

    action = models.CharField(max_length=30, choices=ActionType.choices)
    resource_type = models.CharField(max_length=100, help_text="Ej: ClinicalRecord, SessionNote, MedicalResult")
    resource_id = models.CharField(max_length=100, help_text="UUID o ID del recurso accedido")
    patient_id = models.IntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.user} -- {self.action} -- {self.resource_type}:{self.resource_id}"


# ---------------------------------------------------------------------------
# 4. Gestión de Consentimientos Versionados (requerimiento 2 y 3)
# ---------------------------------------------------------------------------

class ConsentDocument(models.Model):
    """Versioned consent document template managed by the clinic."""
    class DocumentType(models.TextChoices):
        PRIVACY = 'PRIVACY', 'Política de Privacidad'
        TERMS = 'TERMS', 'Términos y Condiciones'
        CLINICAL = 'CLINICAL', 'Consentimiento Clínico'
        OCCUPATIONAL = 'OCCUPATIONAL', 'Consentimiento Ocupacional'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='consent_documents')
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    version = models.CharField(max_length=10, help_text="Ej: v1.0, v2.1")
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_current = models.BooleanField(default=True, help_text="Si True, es la version vigente que deben aceptar los pacientes")
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('clinic', 'document_type', 'version')

    def __str__(self):
        return f"{self.clinic.name} -- {self.document_type} {self.version}"


class PatientConsent(models.Model):
    """Records the patient's acceptance of a specific consent document version."""
    class SignatureMethod(models.TextChoices):
        DIGITAL = 'DIGITAL', 'Firma Digital (portal)'
        TABLET = 'TABLET', 'Firma en Tablet'
        PHYSICAL = 'PHYSICAL', 'Documento Físico'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='consents')
    document = models.ForeignKey(ConsentDocument, on_delete=models.PROTECT, related_name='acceptances')
    accepted_at = models.DateTimeField(auto_now_add=True)
    signed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='signed_consents')
    signature_method = models.CharField(max_length=10, choices=SignatureMethod.choices, default=SignatureMethod.DIGITAL)

    class Meta:
        unique_together = ('patient', 'document')

    def __str__(self):
        return f"{self.patient} -- {self.document}"
