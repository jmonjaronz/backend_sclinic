from django.db import models
import uuid
from core.models import ClinicAwareModel


class Benefit(ClinicAwareModel):
    """
    Discount/benefit defined by the clinic.
    Req: 7_2_Descuentos_Promociones.md
    """
    class BenefitType(models.TextChoices):
        GENERAL = 'GENERAL', 'Descuento General'
        SENIOR = 'SENIOR', 'Adulto Mayor'
        BIRTHDAY = 'BIRTHDAY', 'Descuento Cumpleaños'
        SEASONAL = 'SEASONAL', 'Campaña Temporal'
        PROMO = 'PROMO', 'Promoción'
        RECURRING = 'RECURRING', 'Cliente Frecuente'
        FIRST_VISIT = 'FIRST_VISIT', 'Primera Consulta'

    class DiscountScope(models.TextChoices):
        ALL_SERVICES = 'ALL', 'Todos los Servicios'
        SPECIFIC_SERVICES = 'SERVICES', 'Servicios Específicos'
        SPECIALTY = 'SPECIALTY', 'Especialidad'
        PROTOCOL = 'PROTOCOL', 'Protocolo Médico'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    benefit_type = models.CharField(max_length=20, choices=BenefitType.choices)

    # Discount values
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Scope and priority
    discount_scope = models.CharField(max_length=20, choices=DiscountScope.choices, default=DiscountScope.ALL_SERVICES)
    precedence = models.PositiveIntegerField(default=1, help_text="Mayor valor = mayor prioridad.")
    is_exclusive = models.BooleanField(default=False, help_text="Si True, no se combina con seguros, convenios ni otros descuentos.")

    # Validity (7_2_Descuentos_Promociones.md sec. 4)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)

    # Patient segmentation (7_2_Descuentos_Promociones.md sec. 5)
    min_age = models.PositiveIntegerField(null=True, blank=True)
    max_age = models.PositiveIntegerField(null=True, blank=True)
    min_previous_visits = models.PositiveIntegerField(null=True, blank=True, help_text="Mínimo de visitas previas para aplicar.")

    # Headquarters scope
    applies_to_all_headquarters = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.benefit_type})"


class BenefitService(models.Model):
    """Links a Benefit to specific services when scope is SPECIFIC_SERVICES."""
    benefit = models.ForeignKey(Benefit, on_delete=models.CASCADE, related_name='covered_services')
    service = models.ForeignKey('clinics.Service', on_delete=models.CASCADE, related_name='benefit_covers')

    class Meta:
        unique_together = ('benefit', 'service')


class BenefitHeadquarters(models.Model):
    """Links a Benefit to specific headquarters when applies_to_all_headquarters=False."""
    benefit = models.ForeignKey(Benefit, on_delete=models.CASCADE, related_name='covered_headquarters')
    headquarters = models.ForeignKey('clinics.Headquarters', on_delete=models.CASCADE, related_name='benefit_covers')

    class Meta:
        unique_together = ('benefit', 'headquarters')


class PromoCode(ClinicAwareModel):
    """
    Promotional code that patients can enter to apply a discount.
    Req: 7_2_Descuentos_Promociones.md sec. 11
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, help_text="Código promocional, ej: SALUD2026")
    benefit = models.ForeignKey(Benefit, on_delete=models.CASCADE, related_name='promo_codes')
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Número máximo de usos. Null=ilimitado.")
    current_uses = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_valid(self):
        from django.utils import timezone
        today = timezone.now().date()
        if not self.is_active:
            return False
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_until and today > self.valid_until:
            return False
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        return True

    def __str__(self):
        return f"{self.code} -> {self.benefit.name}"


class BenefitApplicationHistory(models.Model):
    """
    Historical record of when a Benefit was applied to a patient's appointment.
    Req: 7_2_Descuentos_Promociones.md sec. 10
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    benefit = models.ForeignKey(Benefit, on_delete=models.PROTECT, related_name='application_history')
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='benefit_applications')
    service = models.ForeignKey('clinics.Service', on_delete=models.SET_NULL, null=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} | {self.benefit.name} | {self.applied_at.date()}"
