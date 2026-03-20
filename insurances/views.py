from core.viewsets import BaseViewSet
from .models import Insurer, InsurancePlan, InsuranceCoverage
from .serializers import InsurerSerializer, InsurancePlanSerializer, InsuranceCoverageSerializer

class InsurerViewSet(BaseViewSet):
    queryset = Insurer.objects.all()
    serializer_class = InsurerSerializer

class InsurancePlanViewSet(BaseViewSet):
    queryset = InsurancePlan.objects.all()
    serializer_class = InsurancePlanSerializer

class InsuranceCoverageViewSet(BaseViewSet):
    queryset = InsuranceCoverage.objects.all()
    serializer_class = InsuranceCoverageSerializer
