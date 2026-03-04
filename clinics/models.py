from django.db import models
import uuid

class Clinic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    subdomain = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Configuración SaaS
    min_booking_days_notice = models.IntegerField(default=1, help_text="Días mínimos de anticipación para agendar.")
    
    # Reglas de pago
    payment_required_before = models.BooleanField(default=True, help_text="¿Requiere pago previo para confirmar la cita?")
    payment_grace_period_days = models.IntegerField(default=1, help_text="Días antes de la cita para pagar si es requerido.")

    # Reglas de Reprogramación y Anulación
    max_reschedules_allowed = models.IntegerField(default=2, help_text="Límite de veces que se puede reprogramar una cita.")
    reschedule_notice_hours = models.IntegerField(default=24, help_text="Horas mínimas de anticipación para reprogramar.")
    cancel_notice_hours = models.IntegerField(default=24, help_text="Horas mínimas de anticipación para anular.")

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
        OCCUPATIONAL = 'OCCUPATIONAL', 'Salud Ocupacional'
        EMERGENCY = 'EMERGENCY', 'Emergencias'
        HOSPITALIZATION = 'HOSPITALIZATION', 'Hospitalización'

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
    is_confidential_to_patient = models.BooleanField(default=False, help_text="Si es True, el paciente no podrá ver los resultados (ej: pre-empleo).")

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

class SubscriptionPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100) # Ej: Básico, Premium, Ocupacional Pro
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    max_appointments_month = models.IntegerField(default=100)
    max_specialists = models.IntegerField(default=5)
    features = models.JSONField(default=dict, help_text="Configuración de módulos activos (ej: psychological_tests: true)")
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
        ICU = 'ICU', 'Unidad de Cuidados Intensivos (UCI)'
        EMERGENCY = 'EMERGENCY', 'Box de Emergencias'
        SURGICAL = 'SURGICAL', 'Quirófano / Recuperación'
        OTHER = 'OTHER', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    headquarters = models.ForeignKey(Headquarters, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=100) # Ej: Habitación 301
    room_type = models.CharField(max_length=20, choices=RoomType.choices, default=RoomType.GENERAL)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.headquarters.name})"

class Bed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    name = models.CharField(max_length=50) # Ej: Cama A
    is_occupied = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room.name} - {self.name}"
