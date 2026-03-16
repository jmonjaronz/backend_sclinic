from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
import datetime
from .models import Appointment, AvailabilityBlock, TreatmentPlan, AppointmentHistory
from .serializers import AppointmentSerializer, AvailabilityBlockSerializer, TreatmentPlanSerializer, AppointmentHistorySerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    """
    Gestión de citas.
    - Especialistas y Admins ven todas las de su clínica o las suyas propias.
    - Pacientes ven solo sus propias citas.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_qs = Appointment.objects.all()

        if hasattr(user, 'clinic') and user.clinic:
            base_qs = base_qs.filter(clinic=user.clinic)

        if user.role == 'PATIENT':
            return base_qs.filter(patient__user=user)
        elif user.role == 'PSYCHOLOGIST':
            return base_qs.filter(specialist__user=user)
        elif user.role == 'COMPANY' and hasattr(user, 'managed_company'):
            # Ver las citas de todos los empleados de su empresa
            return base_qs.filter(company=user.managed_company)
            
        return base_qs

    def perform_create(self, serializer):
        user = self.request.user
        clinic = serializer.validated_data.get('clinic', getattr(user, 'clinic', None))
        
        extra_data = {'clinic': clinic}
        
        if user.role == 'COMPANY' and hasattr(user, 'managed_company'):
            extra_data['company'] = user.managed_company
            
        serializer.save(**extra_data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def available_slots(self, request):
        """
        Consulta disponibilidad real de slots para un especialista, fecha y servicio.
        """
        specialist_id = request.query_params.get('specialist_id')
        date_str = request.query_params.get('date')
        service_id = request.query_params.get('service_id')
        
        # Priorizar clínica del middleware (multi-tenant)
        clinic = getattr(request, 'clinic', None)
        
        # Fallback a clinic_id solo si no se detectó por host/header
        if not clinic:
            clinic_id = request.query_params.get('clinic_id')
            if clinic_id:
                from core.models import Clinic
                clinic = Clinic.objects.filter(id=clinic_id).first()

        if not all([date_str, clinic]):
            return Response({"error": "Faltan parámetros requeridos (date) o no se detectó la clínica."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Formato de fecha inválido. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        from clinics.models import Specialist, Service
        from .services import check_availability

        specialist = Specialist.objects.filter(id=specialist_id, clinic=clinic).first() if specialist_id else None
        service = Service.objects.filter(id=service_id, clinic=clinic).first() if service_id else None

        # Configuración de slots
        duration = service.duration_minutes if service else 60
        start_hour = 8
        end_hour = 20
        
        available_slots = []
        current_time = datetime.datetime.combine(date_obj, datetime.time(start_hour, 0))
        end_day_time = datetime.datetime.combine(date_obj, datetime.time(end_hour, 0))

        while current_time < end_day_time:
            slot_start = current_time.time()
            slot_end = (current_time + datetime.timedelta(minutes=duration)).time()
            
            is_avail, _ = check_availability(
                clinic=clinic,
                date=date_obj,
                start_time=slot_start,
                end_time=slot_end,
                specialist=specialist,
                service=service
            )
            
            if is_avail:
                available_slots.append(slot_start.strftime("%H:%M"))
            
            current_time += datetime.timedelta(minutes=duration)

        return Response({
            "date": date_str,
            "specialist": specialist.user.get_full_name() if (specialist and getattr(specialist, 'user', None)) else "Cualquiera",
            "service": service.name if service else "General",
            "available_slots": available_slots
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload_voucher(self, request, pk=None):
        """
        Sube un comprobante de pago.
        Cambia el estado de PENDING_PAYMENT a PENDING_VALIDATION.
        """
        appointment = self.get_object()
        user = request.user

        # Validar permisos
        if user.role == 'PATIENT' and appointment.patient.user != user:
            return Response({"error": "No tienes permiso para modificar esta cita."}, status=status.HTTP_403_FORBIDDEN)

        if appointment.status != Appointment.Status.PENDING_PAYMENT:
            return Response({"error": "La cita no está en estado de Pago Pendiente."}, status=status.HTTP_400_BAD_REQUEST)

        voucher = request.FILES.get('payment_voucher')
        if not voucher:
             return Response({"error": "Debe adjuntar una imagen del comprobante (payment_voucher)."}, status=status.HTTP_400_BAD_REQUEST)

        appointment.payment_voucher = voucher
        appointment.status = Appointment.Status.PENDING_VALIDATION
        appointment.voucher_uploaded_at = timezone.now()
        appointment.save()

        return Response({"message": "Comprobante subido exitosamente. En espera de validación administrativa."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def validate_payment(self, request, pk=None):
        """
        El Admin o Staff valida el voucher y confirma la cita.
        """
        appointment = self.get_object()
        user = request.user
        
        if user.role not in ['ADMIN_CLINIC', 'STAFF', 'SUPERADMIN']:
             return Response({"error": "Solo el personal de la clínica puede validar pagos."}, status=status.HTTP_403_FORBIDDEN)

        if appointment.status != Appointment.Status.PENDING_VALIDATION:
             return Response({"error": f"La cita no está pendiente de validación. Estado actual: {appointment.status}"}, status=status.HTTP_400_BAD_REQUEST)

        action = request.data.get('action') # 'approve' or 'reject'

        if action == 'approve':
            appointment.status = Appointment.Status.CONFIRMED
            appointment.validated_by = user
            appointment.validation_date = timezone.now()
            appointment.save()
            return Response({"message": "Pago validado. Cita CONFIRMADA."}, status=status.HTTP_200_OK)
        
        elif action == 'reject':
            rejection_reason = request.data.get('reason', 'Sin motivo especificado.')
            appointment.status = Appointment.Status.PENDING_PAYMENT
            appointment.payment_voucher = None 
            appointment.save()
            return Response({"message": f"Pago rechazado. La cita vuelve a estar Pendiente de Pago. Motivo: {rejection_reason}"}, status=status.HTTP_200_OK)

        return Response({"error": "Debe enviar una 'action' válida ('approve' o 'reject')."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reschedule(self, request, pk=None):
        """
        Reprograma una cita validando límites y plazos de la clínica.
        """
        appointment = self.get_object()
        clinic = appointment.clinic
        user = request.user

        # 1. Validar Límite de Reprogramaciones
        if appointment.reschedule_count >= clinic.max_reschedules_allowed:
            return Response({
                "error": f"Se ha alcanzado el límite máximo de {clinic.max_reschedules_allowed} reprogramaciones para esta clínica."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2. Validar Plazo de Pre-aviso (horas)
        now = timezone.now()
        appointment_dt = timezone.make_aware(datetime.datetime.combine(appointment.date, appointment.start_time))
        diff = appointment_dt - now
        diff_hours = diff.total_seconds() / 3600

        if diff_hours < clinic.reschedule_notice_hours:
            return Response({
                "error": f"La reprogramación debe hacerse con al menos {clinic.reschedule_notice_hours} horas de anticipación. Faltan {diff_hours:.1f}h."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3. Datos de la nueva fecha/hora
        new_date_str = request.data.get('date')
        new_start_time_str = request.data.get('start_time')
        new_end_time_str = request.data.get('end_time')

        if not all([new_date_str, new_start_time_str]):
             return Response({"error": "Debe proporcionar 'date' y 'start_time' para la nueva cita."}, status=status.HTTP_400_BAD_REQUEST)

        # Validar disponibilidad para el nuevo slot (opcionalmente usar el serializer o servicio directamente)
        from .services import check_availability
        new_date = datetime.datetime.strptime(new_date_str, "%Y-%m-%d").date()
        new_start_time = datetime.datetime.strptime(new_start_time_str, "%H:%M").time()
        # Si no envían end_time, calculamos basado en el servicio
        if new_end_time_str:
            new_end_time = datetime.datetime.strptime(new_end_time_str, "%H:%M").time()
        else:
            new_end_time = (datetime.datetime.combine(new_date, new_start_time) + datetime.timedelta(minutes=appointment.service.duration_minutes)).time()

        is_avail, err = check_availability(
            clinic=clinic,
            date=new_date,
            start_time=new_start_time,
            end_time=new_end_time,
            specialist=appointment.specialist,
            service=appointment.service,
            exclude_appointment_id=appointment.id # Importante excluir la cita actual de la validación
        )
        if not is_avail:
            return Response({"error": f"El nuevo horario no está disponible: {err}"}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Registrar Historial y Actualizar
        AppointmentHistory.objects.create(
            appointment=appointment,
            old_status=appointment.status,
            new_status=appointment.status, # El estado no cambia necesariamente
            old_date=appointment.date,
            new_date=new_date,
            old_time=appointment.start_time,
            new_time=new_start_time,
            changed_by=user,
            reason=request.data.get('reason', 'Reprogramación solicitada.')
        )

        appointment.date = new_date
        appointment.start_time = new_start_time
        appointment.end_time = new_end_time
        appointment.reschedule_count += 1
        appointment.is_rescheduled = True
        appointment.save()

        return Response({"message": "Cita reprogramada exitosamente.", "reschedule_count": appointment.reschedule_count}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        """
        Anula una cita validando el plazo de pre-aviso.
        """
        appointment = self.get_object()
        clinic = appointment.clinic
        user = request.user

        if appointment.status in [Appointment.Status.CANCELLED, Appointment.Status.NO_SHOW]:
            return Response({"error": "La cita ya se encuentra anulada o cerrada."}, status=status.HTTP_400_BAD_REQUEST)

        # Validar Plazo de Pre-aviso
        now = timezone.now()
        appointment_dt = timezone.make_aware(datetime.datetime.combine(appointment.date, appointment.start_time))
        diff = appointment_dt - now
        diff_hours = diff.total_seconds() / 3600

        # Solo validar para pacientes, el Staff/Admin puede anular siempre
        if user.role == 'PATIENT' and diff_hours < clinic.cancel_notice_hours:
            return Response({
                "error": f"La anulación debe hacerse con al menos {clinic.cancel_notice_hours} horas de anticipación."
            }, status=status.HTTP_400_BAD_REQUEST)

        reason = request.data.get('reason', 'Anulación solicitada.')
        
        # Registrar Historial
        AppointmentHistory.objects.create(
            appointment=appointment,
            old_status=appointment.status,
            new_status=Appointment.Status.CANCELLED,
            changed_by=user,
            reason=reason
        )

        appointment.status = Appointment.Status.CANCELLED
        appointment.cancellation_reason = reason
        appointment.cancelled_at = now
        appointment.save()

        return Response({"message": "Cita anulada exitosamente."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def history(self, request, pk=None):
        """
        Retorna el historial de cambios de la cita.
        """
        appointment = self.get_object()
        history = appointment.history.all()
        serializer = AppointmentHistorySerializer(history, many=True)
        return Response(serializer.data)


class TreatmentPlanViewSet(viewsets.ModelViewSet):
    serializer_class = TreatmentPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_qs = TreatmentPlan.objects.all()
        if hasattr(user, 'clinic') and user.clinic:
            base_qs = base_qs.filter(clinic=user.clinic)
        return base_qs

    def perform_create(self, serializer):
        clinic = serializer.validated_data.get('clinic', getattr(self.request.user, 'clinic', None))
        serializer.save(clinic=clinic, specialist_creator=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        # Solo el creador o un admin puede editar
        if instance.specialist_creator != self.request.user and self.request.user.role not in ['ADMIN_CLINIC', 'SUPERADMIN']:
             from rest_framework.exceptions import PermissionDenied
             raise PermissionDenied("Solo el especialista que creó el plan puede modificarlo.")
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload_plan_voucher(self, request, pk=None):
        """
        Sube un solo comprobante para pagar TODAS las sesiones de un plan terapéutico.
        Cambia el estado de todas las citas PENDING_PAYMENT del plan a PENDING_VALIDATION.
        """
        plan = self.get_object()
        user = request.user

        # Solo el titular del paciente o admin puede pagar el plan
        if user.role == 'PATIENT' and plan.patient.user != user:
            return Response({'error': 'No tienes permiso para pagar este plan.'}, status=status.HTTP_403_FORBIDDEN)

        voucher = request.FILES.get('payment_voucher')
        if not voucher:
            return Response({'error': 'Debe adjuntar el comprobante de pago (payment_voucher).'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener todas las citas pendientes del plan
        pending_sessions = plan.sessions.filter(status=Appointment.Status.PENDING_PAYMENT)
        count = pending_sessions.count()

        if count == 0:
            return Response({'message': 'No hay sesiones pendientes de pago en este plan.'}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar todas en lote
        now = timezone.now()
        for appt in pending_sessions:
            appt.payment_voucher = voucher
            appt.status = Appointment.Status.PENDING_VALIDATION
            appt.voucher_uploaded_at = now
            appt.payment_modality = Appointment.PaymentModality.VOUCHER
            appt.save()

        # Actualizar el estado del plan a PARTIAL o PAID según sea necesario
        plan.payment_status = TreatmentPlan.PaymentStatus.PARTIAL
        plan.save()

        return Response({
            'message': f'Comprobante subido para {count} sesiones. En espera de validación administrativa.',
            'sessions_updated': count
        }, status=status.HTTP_200_OK)

class AvailabilityBlockViewSet(viewsets.ModelViewSet):
    queryset = AvailabilityBlock.objects.all()
    serializer_class = AvailabilityBlockSerializer
    permission_classes = [permissions.IsAuthenticated]
