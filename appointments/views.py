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
        Endpoint personalizado para consultar disponibilidad.
        Params expected: specialist_id, date, clinic_id
        """
        specialist_id = request.query_params.get('specialist_id')
        date_str = request.query_params.get('date')
        clinic_id = request.query_params.get('clinic_id')

        if not all([specialist_id, date_str, clinic_id]):
            return Response({"error": "Faltan parámetros requeridos (specialist_id, date, clinic_id)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Formato de fecha inválido. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Lógica de cálculo de slots libres... 
        # (Dependería de los horarios de trabajo estándar del especialista, cruzándolos
        # con citas ya existentes y bloqueos de AvailabilityBlock)
        # Por ahora se devuelve un mock up en formato Array de horas.
        
        return Response({
            "message": "Cálculo de slots en desarrollo.",
            "available_slots": ["09:00", "10:00", "12:00", "16:00"]
        })

class TreatmentPlanViewSet(viewsets.ModelViewSet):
    queryset = TreatmentPlan.objects.all()
    serializer_class = TreatmentPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

class AvailabilityBlockViewSet(viewsets.ModelViewSet):
    queryset = AvailabilityBlock.objects.all()
    serializer_class = AvailabilityBlockSerializer
    permission_classes = [permissions.IsAuthenticated]
