#insurances/serializers.py
from rest_framework import serializers
from .models import Insurer, InsurancePlan, InsuranceCoverage

class InsurerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurer
        fields = '__all__'

class InsurancePlanSerializer(serializers.ModelSerializer):
    insurer_name = serializers.ReadOnlyField(source='insurer.name')

    class Meta:
        model = InsurancePlan
        fields = '__all__'

class InsuranceCoverageSerializer(serializers.ModelSerializer):
    service_name = serializers.ReadOnlyField(source='service.name')
    specialty_name = serializers.ReadOnlyField(source='specialty.name')

    class Meta:
        model = InsuranceCoverage
        fields = '__all__'
