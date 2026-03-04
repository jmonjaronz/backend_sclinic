from rest_framework import serializers
from .models import Company, Agreement, Employee

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
    document_number = serializers.CharField(source='patient.user.document_number', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'company', 'patient', 'patient_name', 'document_number',
            'job_title', 'department', 'status', 'hired_at'
        ]
