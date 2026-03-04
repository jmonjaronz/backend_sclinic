from rest_framework import serializers
from django.utils import timezone
from .models import ClinicalRecord, SessionNote
from clinics.models import Specialist
from patients.models import Patient

class SessionNoteSerializer(serializers.ModelSerializer):
    specialist_name = serializers.CharField(source='specialist.user.get_full_name', read_only=True)

    class Meta:
        model = SessionNote
        fields = [
            'id', 'record', 'appointment', 'specialist', 'specialist_name', 'date',
            'session_reason', 'observations', 'diagnosis', 'therapeutic_objective',
            'recommendations', 'commitments', 'assigned_materials', 'next_session_indications',
            'is_locked', 'locked_at'
        ]
        read_only_fields = ['id', 'is_locked', 'locked_at', 'date']

    def update(self, instance, validated_data):
        # Regla de Negocio Crítica: Inmutabilidad
        if instance.is_locked:
            raise serializers.ValidationError(
                "Esta nota de sesión ha sido bloqueada/firmada y no puede ser modificada."
            )
        return super().update(instance, validated_data)


class ClinicalRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    document_number = serializers.CharField(source='patient.document_number', read_only=True)
    session_notes = SessionNoteSerializer(many=True, read_only=True)

    class Meta:
        model = ClinicalRecord
        fields = [
            'id', 'clinic', 'patient', 'patient_name', 'document_number', 
            'assigned_specialists', 'created_at', 'updated_at', 'session_notes'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"
