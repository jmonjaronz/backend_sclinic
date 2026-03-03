from rest_framework import serializers
from .models import B2BCompany, CompanyAffiliation, Benefit

class B2BCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = B2BCompany
        fields = '__all__'

class CompanyAffiliationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAffiliation
        fields = '__all__'

class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = '__all__'
