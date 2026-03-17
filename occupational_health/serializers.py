from rest_framework import serializers
from .models import OccupationalEvaluation, EvaluationServiceStatus, AptitudeDictum

class EvaluationServiceStatusSerializer(serializers.ModelSerializer):
    service_name = serializers.ReadOnlyField(source='protocol_service.service.name')
    
    class Meta:
        model = EvaluationServiceStatus
        fields = '__all__'

class AptitudeDictumSerializer(serializers.ModelSerializer):
    doctor_name = serializers.ReadOnlyField(source='doctor.get_full_name')

    class Meta:
        model = AptitudeDictum
        fields = '__all__'

class OccupationalEvaluationSerializer(serializers.ModelSerializer):
    patient_name = serializers.ReadOnlyField(source='patient.get_full_name')
    company_name = serializers.ReadOnlyField(source='company.razon_social')
    protocol_name = serializers.ReadOnlyField(source='protocol.name')
    service_tracking = EvaluationServiceStatusSerializer(many=True, read_only=True)
    aptitude_dictum = AptitudeDictumSerializer(read_only=True)

    class Meta:
        model = OccupationalEvaluation
        fields = '__all__'
