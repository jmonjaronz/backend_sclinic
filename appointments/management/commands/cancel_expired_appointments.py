from django.core.management.base import BaseCommand
from django.utils import timezone
from appointments.models import Appointment

class Command(BaseCommand):
    help = 'Cancela automáticamente las citas cuyo tiempo límite de pago ha expirado.'

    def handle(self, *args, **options):
        now = timezone.now()
        expired_appointments = Appointment.objects.filter(
            status=Appointment.Status.PENDING_PAYMENT,
            payment_deadline__lt=now
        )

        count = expired_appointments.count()
        for appointment in expired_appointments:
            appointment.status = Appointment.Status.CANCELLED
            appointment.cancellation_reason = "Cancelación automática por falta de pago (tiempo límite expirado)."
            appointment.cancelled_at = now
            appointment.save()

            # Registrar en el historial si es necesario
            from appointments.models import AppointmentHistory
            AppointmentHistory.objects.create(
                appointment=appointment,
                old_status=Appointment.Status.PENDING_PAYMENT,
                new_status=Appointment.Status.CANCELLED,
                reason="Sistema: Pago no recibido dentro del plazo."
            )

        self.stdout.write(self.style.SUCCESS(f'Se han cancelado {count} citas expiradas.'))
