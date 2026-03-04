from rest_framework import viewsets, permissions
from .models import PsychologicalTest, TestApplication
from .serializers import PsychologicalTestSerializer, TestApplicationSerializer

class PsychologicalTestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Catálogo de Tests Psicológicos disponibles.
    Solo lectura para listar estructura, dimensiones, preguntas y opciones.
    """
    queryset = PsychologicalTest.objects.all()
    serializer_class = PsychologicalTestSerializer
    permission_classes = [permissions.IsAuthenticated]

class TestApplicationViewSet(viewsets.ModelViewSet):
    """
    Gestión de Aplicaciones de Tests.
    """
    serializer_class = TestApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_qs = TestApplication.objects.all()

        if hasattr(user, 'clinic') and user.clinic:
            base_qs = base_qs.filter(clinic=user.clinic)

        if user.role == 'PATIENT':
            return base_qs.filter(patient__user=user)
        elif user.role == 'PSYCHOLOGIST':
            return base_qs.filter(specialist__user=user)
            
        return base_qs

    def perform_create(self, serializer):
        # Asignar clínica o permisos predeterminados antes de calcular nota
        clinic = getattr(self.request.user, 'clinic', None)
        serializer.save(clinic=clinic)
