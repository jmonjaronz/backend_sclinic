#clinics/services.py
from django.utils import timezone
from django.db import transaction
from .models import UsageMetric, Subscription
from rest_framework.exceptions import PermissionDenied

class UsageService:
    @staticmethod
    def get_current_period():
        """Retorna el periodo actual en formato YYYY-MM"""
        return timezone.now().strftime("%Y-%m")

    @staticmethod
    def check_and_increment(clinic, metric_code, increment=1):
        """
        Verifica si la clínica tiene cuota disponible para una métrica 
        y la incrementa si es posible.
        """
        period = UsageService.get_current_period()
        
        with transaction.atomic():
            # 1. Obtener la suscripción y el límite del plan
            try:
                subscription = Subscription.objects.select_related('plan').get(clinic=clinic, is_active=True)
                plan = subscription.plan
            except Subscription.DoesNotExist:
                raise PermissionDenied("La clínica no tiene una suscripción activa.")

            # 2. Determinar el límite según el código de métrica
            limit = 0
            if metric_code == 'appointments_monthly':
                limit = plan.max_appointments_month
            elif metric_code == 'specialists_active':
                limit = plan.max_specialists
            else:
                # Si la métrica no está en el plan básico, revisar el JSON de features
                limit = plan.features.get(f'limit_{metric_code}', 0)

            # 3. Obtener o crear la métrica de uso actual
            usage, created = UsageMetric.objects.select_for_update().get_or_create(
                clinic=clinic,
                metric_code=metric_code,
                period=period,
                defaults={'value': 0}
            )

            # 4. Validar
            if usage.value + increment > limit:
                raise PermissionDenied(
                    f"Se ha alcanzado el límite de '{metric_code}' para el plan '{plan.name}' ({limit})."
                )

            # 5. Incrementar
            usage.value += increment
            usage.save()
            
            return usage.value

    @staticmethod
    def get_usage(clinic, metric_code):
        """Obtiene el consumo actual sin incrementar."""
        period = UsageService.get_current_period()
        usage = UsageMetric.objects.filter(clinic=clinic, metric_code=metric_code, period=period).first()
        return usage.value if usage else 0
