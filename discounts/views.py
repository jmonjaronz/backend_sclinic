from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import B2BCompany, CompanyAffiliation, Benefit
from .serializers import B2BCompanySerializer, CompanyAffiliationSerializer, BenefitSerializer
from .logic import calculate_final_price
from patients.models import Patient
from clinics.models import Service

class B2BCompanyViewSet(viewsets.ModelViewSet):
    """
    CRUD para las empresas (Solo ADMIN_CLINIC y SUPERADMIN).
    """
    queryset = B2BCompany.objects.all()
    serializer_class = B2BCompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    # TODO: Implementar permisos más granulares según rol si es necesario.

class CompanyAffiliationViewSet(viewsets.ModelViewSet):
    """
    Gestión de la lista de personas afiliadas (White-list).
    """
    queryset = CompanyAffiliation.objects.all()
    serializer_class = CompanyAffiliationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_affiliation(self, request):
        """
        Endpoint público (o para pacientes) que verifica si un DNI/CE 
        está en la lista de afiliados de alguna empresa con beneficios.
        """
        document_type = request.data.get('document_type')
        document_number = request.data.get('document_number')

        if not document_type or not document_number:
            return Response(
                {"error": "Debe enviar document_type y document_number."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        affiliations = CompanyAffiliation.objects.filter(
            document_type=document_type,
            document_number=document_number,
            company__is_active=True
        )

        if not affiliations.exists():
            return Response({
                "has_affiliation": False,
                "message": "No se encontraron beneficios corporativos activos para este documento."
            }, status=status.HTTP_200_OK)

        # Puede haber múltiples si está en 2 convenios, listamos
        active_benefits = []
        for aff in affiliations:
            company_benefits = Benefit.objects.filter(company=aff.company, is_active=True)
            for b in company_benefits:
                active_benefits.append({
                    "company_name": aff.company.name,
                    "benefit_name": b.name,
                    "discount_percentage": str(b.discount_percentage),
                    "discount_fixed": str(b.discount_fixed),
                    "precedence": b.precedence
                })

        return Response({
            "has_affiliation": True,
            "affiliations": active_benefits
        }, status=status.HTTP_200_OK)

class BenefitViewSet(viewsets.ModelViewSet):
    """
    Gestión de las reglas de descuento.
    """
    queryset = Benefit.objects.all()
    serializer_class = BenefitSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def quote(self, request):
        """
        Calcula el precio final para un paciente y servicio dados,
        aplicando automáticamente el mejor beneficio disponible.

        Body: { "patient_id": <int>, "service_id": <uuid> }
        """
        patient_id = request.data.get('patient_id')
        service_id = request.data.get('service_id')

        if not patient_id or not service_id:
            return Response({'error': 'Se requieren patient_id y service_id.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({'error': 'Paciente no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({'error': 'Servicio no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        result = calculate_final_price(service.price, patient)
        return Response({
            'patient': f"{patient.first_name} {patient.last_name}",
            'service': service.name,
            'original_price': str(result['original_price']),
            'discount_percentage': str(result['discount_percentage']),
            'final_price': str(result['final_price']),
            'benefit_applied': result['benefit_applied']
        }, status=status.HTTP_200_OK)
