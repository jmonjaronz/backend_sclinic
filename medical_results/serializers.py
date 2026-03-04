from rest_framework import serializers
from .models import MedicalResult, LaboratoryDetail

class LaboratoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaboratoryDetail
        fields = ['parameter_name', 'value', 'unit', 'reference_range', 'is_abnormal']

class MedicalResultSerializer(serializers.ModelSerializer):
    details = LaboratoryDetailSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    
    class Meta:
        model = MedicalResult
        fields = [
            'id', 'clinic', 'patient', 'patient_name', 'appointment', 
            'result_type', 'summary', 'attachment', 'performed_at', 
            'created_at', 'details'
        ]
        read_only_fields = ['id', 'created_at']
