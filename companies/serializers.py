from rest_framework import serializers
from .models import Company, Agreement, Employee
from patients.models import Patient
import datetime

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id', 'clinic', 'ruc', 'razon_social', 'address', 
            'contact_person', 'contact_email', 'contact_phone', 
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AgreementSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.razon_social', read_only=True)
    
    class Meta:
        model = Agreement
        fields = [
            'id', 'company', 'company_name', 'clinic', 'name', 
            'discount_percentage', 'benefits_description', 
            'valid_from', 'valid_until', 'is_active'
        ]

class EmployeeSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    document_number = serializers.CharField(source='patient.document_number', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'company', 'patient', 'patient_name', 'document_number',
            'job_title', 'department', 'status', 'hired_at'
        ]

class EmployeeRegistrationSerializer(serializers.Serializer):
    """
    Serializer to register a patient and link them as an employee in one go.
    """
    # Patient Data
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    document_type = serializers.ChoiceField(choices=Patient.DocumentType.choices, default=Patient.DocumentType.DNI)
    document_number = serializers.CharField(max_length=50)
    birth_date = serializers.DateField()
    gender = serializers.ChoiceField(choices=Patient.Gender.choices, required=False)
    
    # Employee Data
    job_title = serializers.CharField(max_length=255, required=False)
    department = serializers.CharField(max_length=255, required=False)
    hired_at = serializers.DateField(required=False)
    
    def create(self, validated_data):
        request = self.context.get('request')
        company = validated_data.get('company') # Managed by the view
        
        # 1. Get or Create Patient
        patient, created = Patient.objects.get_or_create(
            clinic=company.clinic,
            document_type=validated_data['document_type'],
            document_number=validated_data['document_number'],
            defaults={
                'first_name': validated_data['first_name'],
                'last_name': validated_data['last_name'],
                'birth_date': validated_data['birth_date'],
                'gender': validated_data.get('gender', ''),
            }
        )
        
        # 2. Link as Employee
        employee, _ = Employee.objects.get_or_create(
            company=company,
            patient=patient,
            defaults={
                'job_title': validated_data.get('job_title', ''),
                'department': validated_data.get('department', ''),
                'hired_at': validated_data.get('hired_at'),
            }
        )
        
        return employee
