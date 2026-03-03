from rest_framework import viewsets, permissions
from .models import PsychologicalTest, TestApplication
from .serializers import PsychologicalTestSerializer, TestApplicationSerializer

class PsychologicalTestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PsychologicalTest.objects.all()
    serializer_class = PsychologicalTestSerializer
    permission_classes = [permissions.IsAuthenticated]

class TestApplicationViewSet(viewsets.ModelViewSet):
    queryset = TestApplication.objects.all()
    serializer_class = TestApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'SUPERADMIN':
            return self.queryset
        
        if hasattr(user, 'patient_profile'):
            return self.queryset.filter(patient=user.patient_profile)
            
        return self.queryset
