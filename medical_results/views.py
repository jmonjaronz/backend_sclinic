from core.viewsets import BaseViewSet
from .models import MedicalResult
from .serializers import MedicalResultSerializer

class MedicalResultViewSet(BaseViewSet):
    """
    Gestión de Resultados Médicos (Laboratorio e Imágenes).
    """
    serializer_class = MedicalResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_qs = super().get_queryset()

        if user.role == 'PATIENT':
            return base_qs.filter(patient__user=user).exclude(appointment__service__is_confidential_to_patient=True)
        
        if hasattr(user, 'managed_company'):
            # Company managers ONLY see results linked to their company via appointment
            return base_qs.filter(appointment__company=user.managed_company)
        
        return base_qs
