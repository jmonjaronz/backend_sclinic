from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db import models
from .models import PsychologicalTest, TestApplication, TestBattery
from .serializers import PsychologicalTestSerializer, TestApplicationSerializer, TestBatterySerializer

class TestBatteryViewSet(viewsets.ModelViewSet):
    serializer_class = TestBatterySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        clinic = getattr(self.request.user, 'clinic', None)
        if clinic:
            return TestBattery.objects.filter(clinic=clinic)
        return TestBattery.objects.none()

    def perform_create(self, serializer):
        serializer.save(clinic=self.request.user.clinic)

class PsychologicalTestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Catálogo de Tests Psicológicos disponibles.
    """
    queryset = PsychologicalTest.objects.all()
    serializer_class = PsychologicalTestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        clinic = getattr(self.request.user, 'clinic', None)
        return PsychologicalTest.objects.filter(models.Q(clinic=clinic) | models.Q(clinic__isnull=True))

class TestApplicationViewSet(viewsets.ModelViewSet):
    """
    Gestión de Aplicaciones de Tests.
    """
    serializer_class = TestApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        clinic = getattr(user, 'clinic', None)
        base_qs = TestApplication.objects.filter(clinic=clinic)

        if user.role == 'PATIENT':
            return base_qs.filter(patient__user=user)
        
        if hasattr(user, 'managed_company'):
            # Company managers see tests of their employees
            return base_qs.filter(patient__employee_profiles__company=user.managed_company)

        # Specialist/Admin can see tests for their clinic
        return base_qs

    def perform_create(self, serializer):
        clinic = getattr(self.request.user, 'clinic', None)
        serializer.save(clinic=clinic)
