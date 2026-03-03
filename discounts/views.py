from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import B2BCompany, CompanyAffiliation, Benefit
from .serializers import B2BCompanySerializer, CompanyAffiliationSerializer, BenefitSerializer
from .logic import get_best_benefit
from patients.models import Patient

class B2BCompanyViewSet(viewsets.ModelViewSet):
    queryset = B2BCompany.objects.all()
    serializer_class = B2BCompanySerializer
    permission_classes = [permissions.IsAdminUser]

class BenefitViewSet(viewsets.ModelViewSet):
    queryset = Benefit.objects.all()
    serializer_class = BenefitSerializer
    permission_classes = [permissions.IsAdminUser]

class CompanyAffiliationViewSet(viewsets.ModelViewSet):
    queryset = CompanyAffiliation.objects.all()
    serializer_class = CompanyAffiliationSerializer
    permission_classes = [permissions.IsAdminUser]

class DiscountCheckViewSet(viewsets.ViewSet):
    """
    Public-ish endpoint for patients to check their best discount.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_benefit(self, request):
        try:
            patient = request.user.patient_profile
            best_benefit = get_best_benefit(patient)
            
            if not best_benefit:
                return Response({"message": "No aplica ningún beneficio especial por el momento."}, status=status.HTTP_200_OK)
            
            serializer = BenefitSerializer(best_benefit)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": "No se pudo obtener el perfil de paciente"}, status=status.HTTP_400_BAD_REQUEST)
