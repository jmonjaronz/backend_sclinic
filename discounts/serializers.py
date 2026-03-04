from rest_framework import serializers
from .models import B2BCompany, CompanyAffiliation, Benefit

class B2BCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = B2BCompany
        fields = '__all__'

class CompanyAffiliationSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = CompanyAffiliation
        fields = ['id', 'company', 'company_name', 'document_type', 'document_number', 'full_name']

class BenefitSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Benefit
        fields = [
            'id', 'name', 'benefit_type', 'precedence', 
            'discount_percentage', 'discount_fixed', 
            'company', 'company_name', 'is_active'
        ]
