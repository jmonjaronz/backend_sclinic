#companies/serializers.py
from rest_framework import serializers
from .models import Company, Agreement, CompanyEmployee
from patients.models import Patient

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
    patient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CompanyEmployee
        fields = [
            'id', 'company', 'patient', 'patient_name',
            'document_type', 'document_number', 'first_name', 'last_name',
            'job_title', 'department', 'risk_level', 'status', 'hired_at'
        ]

    def get_patient_name(self, obj):
        if obj.patient:
            return f"{obj.patient.first_name} {obj.patient.last_name}"
        return f"{obj.first_name} {obj.last_name}"

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
        
        # 2. Link as CompanyEmployee
        employee, _ = CompanyEmployee.objects.get_or_create(
            company=company,
            document_type=validated_data['document_type'],
            document_number=validated_data['document_number'],
            defaults={
                'patient': patient,
                'first_name': validated_data['first_name'],
                'last_name': validated_data['last_name'],
                'job_title': validated_data.get('job_title', ''),
                'department': validated_data.get('department', ''),
                'hired_at': validated_data.get('hired_at'),
            }
        )
        
        return employee
