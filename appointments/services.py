from django.utils import timezone
import datetime
from django.db.models import Q
from .models import Appointment, AvailabilityBlock

def check_availability(clinic, date, start_time, end_time, specialist=None, service=None, exclude_appointment_id=None):
    """
    Verifica si un horario está disponible considerando bloqueos, capacidad y anticipación.
    Retorna (True, "") o (False, "Motivo")
    """
    # 0. Verificar anticipación mínima (Regla del usuario)
    today = timezone.now().date()
    min_days = clinic.min_booking_days_notice
    min_allowed_date = today + datetime.timedelta(days=min_days + 1)
    
    if date < min_allowed_date:
        return False, f"Las citas deben agendarse con al menos {min_days + 1} días de anticipación. Fecha mínima permitida: {min_allowed_date}"

    # 1. Verificar Bloqueos de Disponibilidad (AvailabilityBlock)
    blocks = AvailabilityBlock.objects.filter(
        clinic=clinic,
        start_date__lte=date,
        end_date__gte=date
    )
    
    # Filtrar por especialista o bloqueos globales de la clínica
    if specialist:
        blocks = blocks.filter(Q(specialist=specialist) | Q(specialist__isnull=True))
    else:
        blocks = blocks.filter(specialist__isnull=True)

    for block in blocks:
        # Verificar día de la semana (0=Lunes, 6=Domingo)
        weekday = str(date.weekday())
        if block.days_of_week and weekday not in block.days_of_week.split(','):
            continue
        
        # Verificar solapamiento de horario si el bloqueo no es de todo el día
        if block.start_time and block.end_time:
            # Hay solapamiento si (start_time < block.end_time) Y (end_time > block.start_time)
            if start_time < block.end_time and end_time > block.start_time:
                return False, f"Horario bloqueado: {block.reason or 'No disponible'}"
        else:
            # Si no tiene horas, es un bloqueo de día completo en ese rango/días
            return False, f"Día bloqueado: {block.reason or 'No disponible'}"

    # 2. Verificar Citas Existentes y Capacidad
    existing_appointments = Appointment.objects.filter(
        clinic=clinic,
        date=date,
        start_time__lt=end_time,
        end_time__gt=start_time,
        status__in=[
            Appointment.Status.CONFIRMED, 
            Appointment.Status.PENDING_PAYMENT, 
            Appointment.Status.PENDING_VALIDATION
        ]
    )

    if exclude_appointment_id:
        existing_appointments = existing_appointments.exclude(id=exclude_appointment_id)

    if service and service.is_simultaneous:
        # Para servicios grupales (talleres, evaluaciones), validamos capacidad
        count = existing_appointments.filter(service=service).count()
        if count >= service.max_capacity:
            return False, f"Capacidad máxima alcanzada para este servicio ({service.max_capacity})."
    else:
        # Para sesiones individuales, el especialista no puede tener otra cita
        if specialist:
            if existing_appointments.filter(specialist=specialist).exists():
                return False, "El especialista ya tiene una cita programada en este horario."
    
    return True, "Disponible"
