#notifications/helpers.py
"""
Helpers para crear notificaciones en-sistema.
Importar y llamar en los puntos donde se disparan eventos.
"""
from .models import Notification


def notify(user, notification_type, title, body):
    """Crea una notificación para el usuario especificado."""
    if user is None:
        return
    Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        body=body
    )


def notify_payment_approved(appointment):
    """Notifica al paciente que su pago fue aprobado."""
    notify(
        user=appointment.patient.user,
        notification_type=Notification.Type.PAYMENT_APPROVED,
        title='Pago Aprobado ✓',
        body=f'Tu pago para la cita del {appointment.date} a las {appointment.start_time} ha sido confirmado. ¡Tu cita está reservada!'
    )


def notify_payment_rejected(appointment, reason=''):
    """Notifica al paciente que su pago fue rechazado."""
    msg = f'Tu comprobante de pago para la cita del {appointment.date} fue rechazado.'
    if reason:
        msg += f' Motivo: {reason}'
    msg += ' Por favor, sube un nuevo comprobante.'
    notify(
        user=appointment.patient.user,
        notification_type=Notification.Type.PAYMENT_REJECTED,
        title='Pago Rechazado ✗',
        body=msg
    )


def notify_plan_approved(treatment_plan):
    """Notifica al paciente que su plan de tratamiento fue aprobado."""
    notify(
        user=treatment_plan.patient.user,
        notification_type=Notification.Type.PLAN_APPROVED,
        title='Plan de Tratamiento Aprobado ✓',
        body=f'Tu plan de {treatment_plan.total_sessions} sesiones ({treatment_plan.service.name}) ha sido confirmado.'
    )


def notify_appointment_reminder(appointment):
    """Recordatorio de cita (invocado por tarea Celery 24h antes)."""
    notify(
        user=appointment.patient.user,
        notification_type=Notification.Type.APPOINTMENT_REMINDER,
        title='Recordatorio de Cita 📅',
        body=f'Tienes una cita mañana {appointment.date} a las {appointment.start_time} — {appointment.service.name}.'
    )
