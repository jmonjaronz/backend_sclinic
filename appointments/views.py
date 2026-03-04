from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
import datetime
from .models import Appointment, AvailabilityBlock, TreatmentPlan
from .serializers import AppointmentSerializer, AvailabilityBlockSerializer, TreatmentPlanSerializer

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
            # Ver las citas donde es especialista
            return base_qs.filter(specialist__user=user)
            
        return base_qs

    def perform_create(self, serializer):
        # Auto-asignar clínica del usuario creador si no se envía
        clinic = serializer.validated_data.get('clinic', getattr(self.request.user, 'clinic', None))
        serializer.save(clinic=clinic)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def available_slots(self, request):
        """
        Consulta disponibilidad real de slots para un especialista, fecha y servicio.
        """
        specialist_id = request.query_params.get('specialist_id')
        date_str = request.query_params.get('date')
        clinic_id = request.query_params.get('clinic_id')
        service_id = request.query_params.get('service_id')

        if not all([date_str, clinic_id]):
            return Response({"error": "Faltan parámetros requeridos (date, clinic_id)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Formato de fecha inválido. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        from clinics.models import Clinic, Specialist, Service
        from .services import check_availability

        clinic = Clinic.objects.filter(id=clinic_id).first()
        specialist = Specialist.objects.filter(id=specialist_id).first() if specialist_id else None
        service = Service.objects.filter(id=service_id).first() if service_id else None

        if not clinic:
            return Response({"error": "Clínica no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # Configuración de slots (esto podría venir de la base de datos más adelante)
        # Por ahora: de 08:00 a 20:00 cada 60 min (u otra duración si el servicio lo indica)
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
            "specialist": specialist.user.get_full_name() if (specialist and specialist.user) else "Cualquiera",
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
            appointment.payment_voucher = None # Opcionalmente borrar el voucher inválido
            appointment.save()
            return Response({"message": f"Pago rechazado. La cita vuelve a estar Pendiente de Pago. Motivo: {rejection_reason}"}, status=status.HTTP_200_OK)

        return Response({"error": "Debe enviar una 'action' válida ('approve' o 'reject')."}, status=status.HTTP_400_BAD_REQUEST)


class TreatmentPlanViewSet(viewsets.ModelViewSet):
    queryset = TreatmentPlan.objects.all()
    serializer_class = TreatmentPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

class AvailabilityBlockViewSet(viewsets.ModelViewSet):
    queryset = AvailabilityBlock.objects.all()
    serializer_class = AvailabilityBlockSerializer
    permission_classes = [permissions.IsAuthenticated]
