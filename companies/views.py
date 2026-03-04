from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company, Agreement, Employee
from .serializers import CompanySerializer, AgreementSerializer, EmployeeSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    """
    Management of B2B companies by Clinics. 
    Companies also use this to view their own profile.
    """
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        clinic = getattr(user, 'clinic', None)
        
        # If user is a company manager, they only see their company
        if hasattr(user, 'managed_company'):
            return Company.objects.filter(id=user.managed_company.id)
            
        # Clinicians see companies registered in their clinic
        return Company.objects.filter(clinic=clinic)

    def perform_create(self, serializer):
        serializer.save(clinic=self.request.user.clinic)

class AgreementViewSet(viewsets.ModelViewSet):
    """
    Agreements management.
    """
    serializer_class = AgreementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        clinic = getattr(user, 'clinic', None)
        
        if hasattr(user, 'managed_company'):
            return Agreement.objects.filter(company=user.managed_company, is_active=True)
            
        return Agreement.objects.filter(clinic=clinic)

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Employee roster for a company.
    """
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if hasattr(user, 'managed_company'):
            return Employee.objects.filter(company=user.managed_company)
            
        clinic = getattr(user, 'clinic', None)
        return Employee.objects.filter(company__clinic=clinic)

    @action(detail=False, methods=['post'])
    def register_bulk(self, request):
        # Placeholder for bulk employee registration (Excel/CSV later)
        return Response({"detail": "Bulk registration not implemented yet."}, status=status.HTTP_510_NOT_EXTENDED)
