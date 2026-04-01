#companies/models.py
from django.db import models
from django.conf import settings
import uuid
from core.models import ClinicAwareModel


class Company(ClinicAwareModel):
    """
    B2B company or institution that contracts medical services for its workers.
    Req: 6_0_GestionEmpresas.md
    """
    class BillingType(models.TextChoices):
        CASH = 'CASH', 'Al Contado'
        CREDIT = 'CREDIT', 'Crédito'

    class CompanyStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Activa'
        INACTIVE = 'INACTIVE', 'Inactiva'
        SUSPENDED = 'SUSPENDED', 'Suspendida'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Identificación legal
    ruc = models.CharField(max_length=20, unique=True, help_text="RUC de la empresa.")
    razon_social = models.CharField(max_length=255, help_text="Razón social registrada.")
    trade_name = models.CharField(max_length=255, blank=True, help_text="Nombre comercial opcional.")
    economic_sector = models.CharField(max_length=100, blank=True, help_text="Rubro o sector económico.")

    # Contacto
    legal_address = models.TextField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    # Configuración comercial (6_0_GestionEmpresas.md sec. 2)
    billing_type = models.CharField(max_length=10, choices=BillingType.choices, default=BillingType.CASH)
    credit_days = models.PositiveIntegerField(default=0, help_text="Días de crédito si aplica.")

    # Estado
    status = models.CharField(max_length=15, choices=CompanyStatus.choices, default=CompanyStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ruc} - {self.razon_social}"


class CompanyUser(models.Model):
    """
    Authorized user from the company who accesses the B2B portal.
    Req: 6_0_GestionEmpresas.md sec. 3
    """
    class CompanyUserRole(models.TextChoices):
        ADMIN_HR = 'ADMIN_HR', 'Administrador RRHH'
        OCCUPATIONAL_DOCTOR = 'OCC_DOCTOR', 'Médico Ocupacional de Empresa'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_users')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_access')
    company_role = models.CharField(max_length=20, choices=CompanyUserRole.choices, default=CompanyUserRole.ADMIN_HR)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('company', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.company.razon_social} ({self.company_role})"


class CompanyProject(models.Model):
    """
    Project or cost center within a company. Workers can be grouped by project.
    Req: 6_0_GestionEmpresas.md sec. 4
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255, help_text="Ej: Proyecto Puente Norte, Mina Azul")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.company.razon_social} - {self.name}"


class CompanyEmployee(models.Model):
    """
    Worker registered under a company, potentially linked to a Patient record.
    Req: 6_0_GestionEmpresas.md sec. 4
    """
    class EmployeeStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Activo'
        INACTIVE = 'INACTIVE', 'Inactivo'
        RETIRED = 'RETIRED', 'Retirado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    # Optional link to a patient record (created on registration if not exists)
    patient = models.ForeignKey('patients.Patient', on_delete=models.SET_NULL, null=True, blank=True, related_name='company_employments')
    project = models.ForeignKey(CompanyProject, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')

    # Identification (for cases where patient record doesn't exist yet)
    document_type = models.CharField(max_length=20, default='DNI')
    document_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # Employment info
    job_title = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    risk_level = models.CharField(max_length=50, blank=True, help_text="Nivel de riesgo ocupacional del puesto.")
    status = models.CharField(max_length=20, choices=EmployeeStatus.choices, default=EmployeeStatus.ACTIVE)
    hired_at = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('company', 'document_type', 'document_number')

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company.razon_social}"


class Agreement(ClinicAwareModel):
    """
    Agreement between a Clinic and a Company.
    Req: 7_1_ConveniosInstitucionales.md
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='agreements')
    name = models.CharField(max_length=255)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    benefits_description = models.TextField(blank=True)
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.company.razon_social} - {self.name}"


class InstitutionServicePrice(models.Model):
    """
    Preferential price for a specific service under an agreement.
    Req: 7_1_ConveniosInstitucionales.md sec. 4
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name='service_prices')
    service = models.ForeignKey('clinics.Service', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ('agreement', 'service')

    def __str__(self):
        return f"{self.agreement.name} -> {self.service.name}: S/ {self.price}"


# ---------------------------------------------------------------------------
# Medical Protocols (Req: 6_1_ProtocolosMedicos.md)
# ---------------------------------------------------------------------------

class MedicalProtocol(ClinicAwareModel):
    """
    A structured package of medical services used for occupational evaluations.
    """
    class EvaluationType(models.TextChoices):
        ENTRY = 'ENTRY', 'Ingreso'
        PERIODIC = 'PERIODIC', 'Periódico'
        EXIT = 'EXIT', 'Retiro'
        OTHER = 'OTHER', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    evaluation_type = models.CharField(max_length=20, choices=EvaluationType.choices, default=EvaluationType.ENTRY)
    version = models.CharField(max_length=10, default='v1.0', help_text="Versión del protocolo. Nuevas versiones se crean como nuevos registros.")
    is_active = models.BooleanField(default=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.version}) - {self.clinic.name}"


class ProtocolService(models.Model):
    """
    A service within a MedicalProtocol, with execution order and required/optional flag.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocol = models.ForeignKey(MedicalProtocol, on_delete=models.CASCADE, related_name='protocol_services')
    service = models.ForeignKey('clinics.Service', on_delete=models.PROTECT, related_name='in_protocols')
    order = models.PositiveIntegerField(default=1, help_text="Orden de ejecución dentro del protocolo.")
    is_required = models.BooleanField(default=True, help_text="Si False, el servicio es opcional o sugerido.")
    is_closing_service = models.BooleanField(default=False, help_text="Si True, es el servicio de cierre (ej: Consulta Médica Ocupacional). La aptitud solo se puede emitir tras completarlo.")
    estimated_duration_minutes = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order']
        unique_together = ('protocol', 'service')

    def __str__(self):
        return f"{self.protocol.name} - Paso {self.order}: {self.service.name}"


class ProtocolCompanyPrice(models.Model):
    """
    Company-specific price for a protocol (different from the base price).
    Req: 6_1_ProtocolosMedicos.md sec. 3
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocol = models.ForeignKey(MedicalProtocol, on_delete=models.CASCADE, related_name='company_prices')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='protocol_prices')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('protocol', 'company')

    def __str__(self):
        return f"{self.company.razon_social} -> {self.protocol.name}: S/ {self.price}"


class EmployeeProtocolAssignment(models.Model):
    """
    Assigns a MedicalProtocol to a CompanyEmployee.
    """
    class AssignmentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        IN_PROGRESS = 'IN_PROGRESS', 'En Progreso'
        COMPLETED = 'COMPLETED', 'Completado'
        CANCELLED = 'CANCELLED', 'Cancelado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(CompanyEmployee, on_delete=models.CASCADE, related_name='protocol_assignments')
    protocol = models.ForeignKey(MedicalProtocol, on_delete=models.PROTECT, related_name='employee_assignments')
    status = models.CharField(max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.PENDING)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee} -> {self.protocol.name} ({self.status})"
