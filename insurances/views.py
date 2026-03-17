from rest_framework import viewsets
from .models import Insurer, InsurancePlan, InsuranceCoverage
from .serializers import InsurerSerializer, InsurancePlanSerializer, InsuranceCoverageSerializer

class InsurerViewSet(viewsets.ModelViewSet):
    queryset = Insurer.objects.all()
    serializer_class = InsurerSerializer

class InsurancePlanViewSet(viewsets.ModelViewSet):
    queryset = InsurancePlan.objects.all()
    serializer_class = InsurancePlanSerializer

class InsuranceCoverageViewSet(viewsets.ModelViewSet):
    queryset = InsuranceCoverage.objects.all()
    serializer_class = InsuranceCoverageSerializer
