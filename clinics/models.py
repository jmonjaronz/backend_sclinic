from django.db import models
import uuid
from django.conf import settings
from core.models import Clinic, ClinicAwareModel


class Headquarters(ClinicAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.clinic.name}"


class Specialty(ClinicAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Specialties"

    def __str__(self):
        return f"{self.name} ({self.clinic.name})"


class Service(ClinicAwareModel):
    """
    Medical service from the clinic catalog.
    Req: 5_CatalogoServicios.md
    """
    class ServiceType(models.TextChoices):
        B2B = 'B2B', 'Corporativo B2B'
        WELLNESS = 'WELLNESS', 'Bienestar'
        OCCUPATIONAL = 'OCCUPATIONAL', 'Salud Ocupacional'
        EMERGENCY = 'EMERGENCY', 'Emergencias'
        HOSPITALIZATION = 'HOSPITALIZATION', 'Hospitalización'
        GENERAL = 'GENERAL', 'Consulta General'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    internal_name = models.CharField(max_length=255, blank=True)
    service_type = models.CharField(max_length=20, choices=ServiceType.choices, default=ServiceType.GENERAL)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Duración y capacidad (5_CatalogoServicios.md)
    duration_minutes = models.PositiveIntegerField(default=30, help_text="Duración base de la consulta en minutos.")
    buffer_minutes = models.PositiveIntegerField(default=5, help_text="Minutos de buffer entre citas.")
    max_patients = models.PositiveIntegerField(default=1, help_text="Capacidad máxima de pacientes por cita (1=individual, >1=grupal).")

    # Instrucciones y requerimientos
    preparation_instructions = models.TextField(blank=True, help_text="Instrucciones previas para el paciente (ej: asistir en ayunas).")
    cancel_notice_hours = models.PositiveIntegerField(default=24, help_text="Horas mínimas de anticipacion para cancelar sin penalidad.")

    # Reglas clínicas
    requires_triage = models.BooleanField(default=False, help_text="Si True, el paciente pasa por Triaje antes de la consulta.")
    is_simultaneous = models.BooleanField(default=False)
    is_confidential_to_patient = models.BooleanField(default=False, help_text="Si True, el paciente no puede ver los resultados (ej: pre-empleo).")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.clinic.name}"


class Specialist(ClinicAwareModel):
    """
    Specialist professional profile. Req: 4_Especialistas.md
    """
    class SpecialistType(models.TextChoices):
        INTERNAL = 'INTERNAL', 'Interno'
        EXTERNAL = 'EXTERNAL', 'Externo'
        AGREEMENT = 'AGREEMENT', 'Por Convenio'

    class SpecialistStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Activo'
        INACTIVE = 'INACTIVE', 'Inactivo (ya no atiende)'
        SUSPENDED = 'SUSPENDED', 'Suspendido'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='specialist_profile')
    specialties = models.ManyToManyField(Specialty, related_name='specialists')
    services = models.ManyToManyField(Service, blank=True, related_name='authorized_specialists', help_text="Servicios que este especialista está autorizado a brindar.")

    # Datos profesionales (4_Especialistas.md)
    specialist_type = models.CharField(max_length=20, choices=SpecialistType.choices, default=SpecialistType.INTERNAL)
    status = models.CharField(max_length=20, choices=SpecialistStatus.choices, default=SpecialistStatus.ACTIVE)
    license_number = models.CharField(max_length=50, blank=True, help_text="Número de colegiatura profesional.")
    professional_college = models.CharField(max_length=100, blank=True, help_text="Colegio profesional (ej: CMP, CPSP).")
    sub_specialty = models.CharField(max_length=100, blank=True, help_text="Subespecialidad (ej: Cardiología).")
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)

    # Perfil público (visible para pacientes)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='specialist_photos/', null=True, blank=True)
    signature_photo = models.ImageField(upload_to='specialist_signatures/', null=True, blank=True, help_text="Imagen de la firma física escaneada.")
    digital_signature_hash = models.CharField(max_length=255, blank=True, help_text="Hash único para validación de firma digital.")
    languages = models.CharField(max_length=255, blank=True, help_text="Idiomas que habla el especialista.")
    keywords = models.CharField(max_length=500, blank=True, help_text="Palabras clave o áreas de especialización.")

    # Visibility / Perfil Dual (Req: 4_Especialistas.md sec. 4)
    is_public = models.BooleanField(default=True, help_text="Si True, es visible en el portal del paciente.")
    is_internal = models.BooleanField(default=True, help_text="Si True, es visible para el personal administrativo interno.")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.clinic.name})"


class SpecialistSchedule(models.Model):
    """
    Weekly base schedule for a specialist.
    """
    class Modality(models.TextChoices):
        PRESENTIAL = 'PRESENTIAL', 'Presencial'
        VIRTUAL = 'VIRTUAL', 'Virtual'
        BOTH = 'BOTH', 'Ambas'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='schedules')
    headquarters = models.ForeignKey(Headquarters, on_delete=models.CASCADE, null=True, blank=True, related_name='schedules')

    day_of_week = models.IntegerField(choices=[(i, str(i)) for i in range(7)], help_text="0=Lunes, 6=Domingo")
    start_time = models.TimeField()
    end_time = models.TimeField()
    modality = models.CharField(max_length=15, choices=Modality.choices, default=Modality.PRESENTIAL)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.specialist} - Día {self.day_of_week} ({self.start_time}-{self.end_time})"


class SpecialistBlock(models.Model):
    """
    Exception block on a specialist's schedule (vacations, sick leave, meetings).
    Req: 4_Especialistas.md sec. 6 - Gestión de Bloqueos y Excepciones.
    """
    class BlockType(models.TextChoices):
        VACATION = 'VACATION', 'Vacaciones / Licencia'
        PERSONAL = 'PERSONAL', 'Asunto Personal'
        MEETING = 'MEETING', 'Reunión Interna'
        TRAINING = 'TRAINING', 'Capacitación / Congreso'
        OTHER = 'OTHER', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='specialist_blocks')
    block_type = models.CharField(max_length=20, choices=BlockType.choices)
    reason = models.CharField(max_length=255, blank=True)

    # Alcance del bloqueo (puede ser todo el día o un rango de horas)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    affects_all_headquarters = models.BooleanField(default=True)
    headquarters = models.ForeignKey(Headquarters, on_delete=models.CASCADE, null=True, blank=True)

    # Auditoría
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_blocks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bloqueo {self.specialist}: {self.start_datetime} - {self.end_datetime}"


class SubscriptionPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    max_appointments_month = models.IntegerField(default=100)
    max_specialists = models.IntegerField(default=5)
    max_headquarters = models.IntegerField(default=1)
    features = models.JSONField(default=dict, help_text="Configuración de módulos activos")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.OneToOneField(Clinic, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.clinic.name} - {self.plan.name}"


class Room(models.Model):
    class RoomType(models.TextChoices):
        GENERAL = 'GENERAL', 'Cuidado General'
        ICU = 'ICU', 'Unidad de Cuidados Intensivos'
        EMERGENCY = 'EMERGENCY', 'Box de Emergencias'
        SURGICAL = 'SURGICAL', 'Quirófano'
        CONSULTATION = 'CONSULTATION', 'Consultorio'
        OTHER = 'OTHER', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    headquarters = models.ForeignKey(Headquarters, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20, choices=RoomType.choices, default=RoomType.CONSULTATION)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.headquarters.name})"


class Bed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    name = models.CharField(max_length=50)
    is_occupied = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room.name} - {self.name}"


class Equipment(ClinicAwareModel):
    """
    Medical equipment or specialized machines (Req: 5_CatalogoServicios.md).
    E.g. ECG, X-Ray, Dental Chair.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    headquarters = models.ForeignKey(Headquarters, on_delete=models.CASCADE, related_name='equipments')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.headquarters.name}"


class ServiceResourceRequirement(models.Model):
    """
    Resources required for a service to be performed.
    Req: 5_CatalogoServicios.md sec. 6
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='resource_requirements')
    
    # Can require a specific room type or specific equipment
    room_type = models.CharField(max_length=20, choices=Room.RoomType.choices, null=True, blank=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True)
    
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        target = self.equipment.name if self.equipment else f"Sala {self.get_room_type_display()}"
        return f"Req para {self.service.name}: {target}"


class ServiceConsentRequirement(models.Model):
    """
    Links a service to a specific versioned consent document.
    Req: 5_CatalogoServicios.md sec. 5
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='consent_requirements')
    consent_document = models.ForeignKey('users.ConsentDocument', on_delete=models.PROTECT)
    
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        unique_together = ('service', 'consent_document')

    def __str__(self):
        return f"Consentimiento {self.consent_document.title} para {self.service.name}"


class FeatureFlag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="Ej: module_laboratory, module_psychology")
    description = models.TextField(blank=True)
    is_active_globally = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ClinicModuleSubscription(ClinicAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(FeatureFlag, on_delete=models.CASCADE, related_name='clinic_subscriptions')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('clinic', 'module')

    def __str__(self):
        return f"{self.clinic.name} - {self.module.name} ({self.is_active})"


class DynamicBrandingEngine(ClinicAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    logo_url = models.ImageField(upload_to='clinic_logos/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default='#000000')
    secondary_color = models.CharField(max_length=7, default='#FFFFFF')
    nomenclature_patient = models.CharField(max_length=50, default='Paciente')
    nomenclature_specialist = models.CharField(max_length=50, default='Especialista')

    def __str__(self):
        return f"Branding de {self.clinic.name}"


class ServiceClinicalRestriction(ClinicAwareModel):
    """
    Sets constraints between appointments of the same patient.
    Req: 8_Agenda.md sec. 12 - Restricciones Clínicas entre Citas
    """
    specialty_a = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='restrictions_as_a')
    specialty_b = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='restrictions_as_b')
    
    min_gap_days = models.PositiveIntegerField(default=1, help_text="Mínimo de días entre citas de estas especialidades.")
    max_gap_days = models.PositiveIntegerField(null=True, blank=True, help_text="Máximo de días permitidos entre citas (si aplica).")
    
    message_error = models.CharField(max_length=255, blank=True, help_text="Mensaje a mostrar si se viola la restricción.")

    class Meta:
        unique_together = ('clinic', 'specialty_a', 'specialty_b')

    def __str__(self):
        return f"Restricción {self.specialty_a.name} -> {self.specialty_b.name} ({self.min_gap_days} d)"


class UsageMetric(ClinicAwareModel):
    """
    Rastreo del consumo de recursos para validación de cuotas.
    Req: 1_Infraestructura.md sec. 4.9
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric_code = models.CharField(max_length=50, help_text="Ej: appointments_monthly, specialists_active")
    value = models.PositiveIntegerField(default=0)
    period = models.CharField(max_length=20, help_text="Ej: 2026-03, ALL_TIME")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('clinic', 'metric_code', 'period')

    def __str__(self):
        return f"{self.clinic.name} - {self.metric_code} ({self.period}): {self.value}"
