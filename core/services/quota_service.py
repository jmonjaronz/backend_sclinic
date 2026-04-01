#core/services/quota_service.py
"""
QuotaService – Validación transaccional de cuotas mensuales.
Req: 1_Infraestructura.md sec. 4.9 – Sistema de Contenedor de Quotas.

Nota: UsageMetric usa el campo `period` como string en formato 'YYYY-MM'.
"""
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied


def _current_period() -> str:
    """Retorna el período actual en formato 'YYYY-MM'."""
    now = timezone.now()
    return f"{now.year}-{now.month:02d}"


class QuotaService:
    """
    Valida y controla el uso de cuotas mensuales en tiempo real.
    Utiliza select_for_update() para prevenir race conditions en entornos concurrentes.

    Compatible con el modelo UsageMetric existente en clinics.models (campo period: str).
    Para uso simple en appointments, se puede seguir usando UsageService.check_and_increment
    de clinics.services. QuotaService extiende con la validación de límites.
    """

    # Códigos de métricas estándar
    APPOINTMENTS_MONTHLY = "appointments_monthly"
    CLINICAL_RECORDS = "clinical_records_created"
    ACTIVE_PATIENTS = "active_patients"

    @staticmethod
    def assert_quota_not_exceeded(clinic, metric_code: str, limit: int):
        """
        Verifica si la clínica ha alcanzado su límite mensual para una métrica dada.
        Lanza PermissionDenied si se ha superado la cuota. NO incrementa el contador.

        Uso en perform_create:
            QuotaService.assert_quota_not_exceeded(clinic, QuotaService.APPOINTMENTS_MONTHLY, 1000)
        """
        if not clinic:
            raise PermissionDenied("Contexto de clínica requerido para validar cuotas.")

        period = _current_period()

        with transaction.atomic():
            try:
                from clinics.models import UsageMetric
            except ImportError:
                return  # Si el modelo no existe aún, permitir sin bloquear

            metric = (
                UsageMetric.global_objects
                .select_for_update()
                .filter(clinic=clinic, metric_code=metric_code, period=period)
                .first()
            )

            if metric and metric.value >= limit:
                raise PermissionDenied(
                    f"Has alcanzado el límite mensual de {limit} para '{metric_code}' "
                    f"(período {period}). Contacta con soporte para ampliar tu plan."
                )

    @staticmethod
    def increment(clinic, metric_code: str, amount: int = 1):
        """
        Incrementa atómicamente el contador de uso mensual.
        Llamar DESPUÉS de una creación exitosa.
        """
        if not clinic:
            return

        period = _current_period()

        try:
            from clinics.models import UsageMetric
        except ImportError:
            return

        with transaction.atomic():
            metric, _ = (
                UsageMetric.global_objects
                .select_for_update()
                .get_or_create(
                    clinic=clinic,
                    metric_code=metric_code,
                    period=period,
                    defaults={"value": 0},
                )
            )
            metric.value += amount
            metric.save(update_fields=["value"])

    @staticmethod
    def get_usage(clinic, metric_code: str) -> int:
        """Retorna el uso actual del mes para una métrica."""
        period = _current_period()
        try:
            from clinics.models import UsageMetric
        except ImportError:
            return 0

        metric = UsageMetric.global_objects.filter(
            clinic=clinic,
            metric_code=metric_code,
            period=period,
        ).first()
        return metric.value if metric else 0
