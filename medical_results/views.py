from rest_framework import viewsets, permissions
from .models import MedicalResult
from .serializers import MedicalResultSerializer

class MedicalResultViewSet(viewsets.ModelViewSet):
    """
    Gestión de Resultados Médicos (Laboratorio e Imágenes).
    """
    serializer_class = MedicalResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        clinic = getattr(user, 'clinic', None)
        base_qs = MedicalResult.objects.filter(clinic=clinic)

        if user.role == 'PATIENT':
            return base_qs.filter(patient__user=user)
        
        return base_qs

    def perform_create(self, serializer):
        clinic = getattr(self.request.user, 'clinic', None)
        serializer.save(clinic=clinic)
