from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import Appointment, AvailabilityBlock, TreatmentPlan
from .serializers import AppointmentSerializer, AvailabilityBlockSerializer, TreatmentPlanSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter by clinic for multi-tenancy
        user = self.request.user
        if user.is_staff or user.role == 'SUPERADMIN':
            return self.queryset
        return self.queryset.filter(clinic=user.clinic)

    def perform_create(self, serializer):
        # Automatically assign clinic from user if not provided
        if not serializer.validated_data.get('clinic'):
            serializer.save(clinic=self.request.user.clinic)
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def validate_payment(self, request, pk=None):
        """
        Action for clinic staff to confirm a payment voucher.
        """
        appointment = self.get_object()
        if appointment.status != Appointment.Status.PENDING_VALIDATION:
            return Response({"error": "La cita no está en espera de validación de pago."}, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid = request.data.get('is_valid', True)
        if is_valid:
            appointment.status = Appointment.Status.CONFIRMED
            appointment.validated_by = request.user
            appointment.validation_date = timezone.now()
            appointment.save()
            return Response({"message": "Pago validado y cita confirmada."})
        else:
            # Revert to pending payment or cancel? Per requirements, let's keep it simple
            appointment.status = Appointment.Status.PENDING_PAYMENT
            appointment.save()
            return Response({"message": "Pago rechazado. La cita vuelve a estado pendiente de pago."})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload_voucher(self, request, pk=None):
        """
        Action for patients to upload their payment voucher.
        """
        appointment = self.get_object()
        voucher = request.FILES.get('payment_voucher')
        if not voucher:
            return Response({"error": "Debe subir un archivo de imagen."}, status=status.HTTP_400_BAD_REQUEST)
        
        appointment.payment_voucher = voucher
        appointment.status = Appointment.Status.PENDING_VALIDATION
        appointment.voucher_uploaded_at = timezone.now()
        appointment.save()
        return Response({"message": "Comprobante subido exitosamente. En espera de validación administrativa."})

class AvailabilityBlockViewSet(viewsets.ModelViewSet):
    queryset = AvailabilityBlock.objects.all()
    serializer_class = AvailabilityBlockSerializer
    permission_classes = [permissions.IsAuthenticated] # Should be restricted to ADMIN_CLINIC

class TreatmentPlanViewSet(viewsets.ModelViewSet):
    queryset = TreatmentPlan.objects.all()
    serializer_class = TreatmentPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def book_sessions(self, request, pk=None):
        """
        Creates multiple appointments for a Treatment Plan.
        Expects a list of slots: [{"date": "YYYY-MM-DD", "start_time": "HH:MM", "end_time": "HH:MM"}]
        """
        plan = self.get_object()
        slots = request.data.get('slots', [])
        
        if len(slots) > plan.total_sessions:
            return Response({"error": f"No puede agendar más de {plan.total_sessions} sesiones."}, status=status.HTTP_400_BAD_REQUEST)
        
        appointments_serializers = []
        for slot in slots:
            serializer = AppointmentSerializer(data={
                **slot,
                'clinic': plan.clinic.id,
                'patient': plan.patient.id,
                'service': plan.service.id,
                'specialist': plan.specialist.id,
                'status': Appointment.Status.PENDING_PAYMENT 
            }, context={'request': request})
            
            if serializer.is_valid():
                appointments_serializers.append(serializer)
            else:
                return Response({
                    "error": f"Error en el horario {slot.get('date')} {slot.get('start_time')}",
                    "details": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # If all valid, save
        created = [s.save() for s in appointments_serializers]
        return Response({
            "message": f"{len(created)} sesiones agendadas exitosamente.",
            "appointments": [a.id for a in created]
        }, status=status.HTTP_201_CREATED)
