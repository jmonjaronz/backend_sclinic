#medical_results/views.py
from core.viewsets import BaseViewSet
from core.mixins import ClinicalAuditReadMixin
from rest_framework import permissions
from .models import MedicalResult
from .serializers import MedicalResultSerializer

class MedicalResultViewSet(ClinicalAuditReadMixin, BaseViewSet):
    """
    Gestión de Resultados Médicos (Laboratorio e Imágenes).
    """
    serializer_class = MedicalResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_audit_patient_id(self, instance):
        return instance.patient.id if instance.patient else None
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
