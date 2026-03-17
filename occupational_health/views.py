from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import OccupationalEvaluation, EvaluationServiceStatus, AptitudeDictum
from .serializers import OccupationalEvaluationSerializer, EvaluationServiceStatusSerializer, AptitudeDictumSerializer
from .services import OccupationalHealthService

class OccupationalEvaluationViewSet(viewsets.ModelViewSet):
    queryset = OccupationalEvaluation.objects.all()
    serializer_class = OccupationalEvaluationSerializer

    @action(detail=True, methods=['post'])
    def initialize_from_protocol(self, request, pk=None):
        evaluation = self.get_object()
        services_created = OccupationalHealthService.initialize_evaluation_services(evaluation)
        return Response({'status': f'{services_created} services tracked from protocol.'})

class EvaluationServiceStatusViewSet(viewsets.ModelViewSet):
    queryset = EvaluationServiceStatus.objects.all()
    serializer_class = EvaluationServiceStatusSerializer

class AptitudeDictumViewSet(viewsets.ModelViewSet):
    queryset = AptitudeDictum.objects.all()
    serializer_class = AptitudeDictumSerializer
