#appointments/services.py
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
            
        # 1.1. Verificar Recurrencia Compleja (ej. Cada 2 semanas)
        # Asumimos que block tiene un campo 'week_interval' y 'start_date' como base
        # Nota: Si el modelo no tiene week_interval, esta lógica es preventiva o requiere cambio en modelo.
        # Según el requerimiento "cada 2 semanas", implementamos el cálculo de intervalo:
        if hasattr(block, 'week_interval') and block.week_interval > 1:
            delta_days = (date - block.start_date).days
            weeks_elapsed = delta_days // 7
            if weeks_elapsed % block.week_interval != 0:
                continue

        # Verificar solapamiento de horario si el bloqueo no es de todo el día
        if block.start_time and block.end_time:
            # Hay solapamiento si (start_time < block.end_time) Y (end_time > block.start_time)
            if start_time < block.end_time and end_time > block.start_time:
                return False, f"Horario bloqueado: {block.reason or 'No disponible'}"
        else:
            # Si no tiene horas, es un bloqueo de día completo en ese rango/días
            return False, f"Día bloqueado: {block.reason or 'No disponible'}"

    # 1.5. Verificar Horario Base (SpecialistSchedule) - Solo si se especifica especialista
    if specialist:
        from clinics.models import SpecialistSchedule
        weekday = date.weekday()
        schedules = SpecialistSchedule.objects.filter(
            specialist=specialist,
            day_of_week=weekday,
            is_active=True
        )
        
        if not schedules.exists():
            return False, "El especialista no atiende en el día seleccionado."
            
        # Verificar si el slot está dentro de alguno de sus turnos
        in_schedule = False
        for sch in schedules:
            if start_time >= sch.start_time and end_time <= sch.end_time:
                in_schedule = True
                break
        
        if not in_schedule:
            return False, "El horario seleccionado está fuera del turno laboral del especialista."

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

class AppointmentService:
    """
    Handles complex status transitions and flow logic for appointments.
    Req: 9_Admision_Triaje.md
    """
    
    @staticmethod
    def process_check_in(appointment):
        """
        Handles the arrival of the patient at the clinic.
        Determines if triage is needed based on service configuration.
        """
        if appointment.status != Appointment.Status.CONFIRMED:
            # If it was PENDING_PAYMENT, we assume payment was validated at reception
            appointment.status = Appointment.Status.CONFIRMED
            
        # Check if service requires triage
        if appointment.service.requires_triage:
            appointment.status = Appointment.Status.WAITING_TRIAGE
        else:
            appointment.status = Appointment.Status.WAITING_CONSULTATION
            
        appointment.save()
        return appointment.status

    @staticmethod
    def complete_triage(appointment, specialist=None):
        """
        Called after nurse completes VitalSigns.
        Moves patient to doctor's waiting room.
        """
        if appointment.status == Appointment.Status.IN_TRIAGE or appointment.status == Appointment.Status.WAITING_TRIAGE:
            appointment.status = Appointment.Status.WAITING_CONSULTATION
            appointment.save()
        return appointment.status
