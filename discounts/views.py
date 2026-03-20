from core.viewsets import BaseViewSet
from .models import Benefit
from .serializers import BenefitSerializer
from .logic import calculate_final_price
from patients.models import Patient
from clinics.models import Service

class BenefitViewSet(BaseViewSet):
    """
    Gestión de las reglas de descuento.
    """
    queryset = Benefit.objects.all()
    serializer_class = BenefitSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def quote(self, request):
        """
        Calcula el precio final para un paciente y servicio dados,
        aplicando automáticamente el mejor beneficio disponible.

        Body: { "patient_id": <int>, "service_id": <uuid> }
        """
        patient_id = request.data.get('patient_id')
        service_id = request.data.get('service_id')

        if not patient_id or not service_id:
            return Response({'error': 'Se requieren patient_id y service_id.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({'error': 'Paciente no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({'error': 'Servicio no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        result = calculate_final_price(service.price, patient)
        return Response({
            'patient': f"{patient.first_name} {patient.last_name}",
            'service': service.name,
            'original_price': str(result['original_price']),
            'discount_percentage': str(result['discount_percentage']),
            'final_price': str(result['final_price']),
            'benefit_applied': result['benefit_applied']
        }, status=status.HTTP_200_OK)

