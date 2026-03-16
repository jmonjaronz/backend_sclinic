from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company, Agreement, CompanyEmployee
from .serializers import CompanySerializer, AgreementSerializer, EmployeeSerializer, EmployeeRegistrationSerializer

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
            return CompanyEmployee.objects.filter(company=user.managed_company)
            
        clinic = getattr(user, 'clinic', None)
        return CompanyEmployee.objects.filter(company__clinic=clinic)

    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeRegistrationSerializer
        return EmployeeSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'managed_company'):
            company = user.managed_company
        else:
            # For Clinicians: they must provide 'company' ID in the request
            company_id = self.request.data.get('company')
            company = Company.objects.get(id=company_id, clinic=user.clinic)
        
        serializer.save(company=company)

    @action(detail=False, methods=['post'])
    def register_bulk(self, request):
        """
        Bulk employee registration via Excel or CSV.
        Expected columns: first_name, last_name, document_type, document_number, birth_date (YYYY-MM-DD), gender, job_title, department
        """
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No se subió ningún archivo."}, status=status.HTTP_400_BAD_REQUEST)

        import pandas as pd
        import io

        try:
            if file_obj.name.endswith('.csv'):
                df = pd.read_csv(io.StringIO(file_obj.read().decode('utf-8')))
            else:
                df = pd.read_excel(file_obj)
        except Exception as e:
            return Response({"error": f"Error al leer el archivo: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if hasattr(user, 'managed_company'):
            company = user.managed_company
        else:
            company_id = request.data.get('company')
            if not company_id:
                return Response({"error": "Debe especificar el ID de la empresa ('company')."}, status=status.HTTP_400_BAD_REQUEST)
            company = Company.objects.filter(id=company_id, clinic=user.clinic).first()
            if not company:
                return Response({"error": "Empresa no encontrada o sin permisos."}, status=status.HTTP_404_NOT_FOUND)

        success_count = 0
        errors = []

        for index, row in df.iterrows():
            serializer_data = {
                'first_name': row.get('first_name'),
                'last_name': row.get('last_name'),
                'document_type': row.get('document_type', 'DNI'),
                'document_number': str(row.get('document_number')),
                'birth_date': row.get('birth_date'),
                'gender': row.get('gender', ''),
                'job_title': row.get('job_title', ''),
                'department': row.get('department', ''),
            }
            
            serializer = EmployeeRegistrationSerializer(data=serializer_data, context={'request': request})
            if serializer.is_valid():
                serializer.save(company=company)
                success_count += 1
            else:
                errors.append({"row": index + 2, "errors": serializer.errors})

        return Response({
            "message": f"Se registraron {success_count} empleados exitosamente.",
            "total_rows": len(df),
            "errors": errors
        }, status=status.HTTP_201_CREATED if success_count > 0 else status.HTTP_400_BAD_REQUEST)
