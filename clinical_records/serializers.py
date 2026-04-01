#clinical_records/serializers.py
from rest_framework import serializers
from .models import (
    ClinicalRecord, SessionNote, EmergencyAdmission, Hospitalization, Treatment, 
    VitalSigns, PrenatalControl, NeonatalControl, Prescription, PrescriptionItem
)

class SessionNoteSerializer(serializers.ModelSerializer):
    specialist_name = serializers.CharField(source='specialist.user.get_full_name', read_only=True)

    class Meta:
        model = SessionNote
        fields = [
            'id', 'record', 'appointment', 'specialist', 'specialist_name', 'date',
            'template', 'dynamic_data',
            'session_reason', 'observations', 'diagnosis', 'therapeutic_objective',
            'recommendations', 'commitments', 'assigned_materials', 'next_session_indications',
            'is_locked', 'locked_at'
        ]
        read_only_fields = ['id', 'is_locked', 'locked_at', 'date']

    def validate(self, data):
        """
        Valida que dynamic_data cumpla con el esquema definido en el template.
        """
        template = data.get('template')
        dynamic_data = data.get('dynamic_data')

        if template and dynamic_data:
            import jsonschema
            from jsonschema import validate
            try:
                # El campo schema en HCETemplate es un JSON que debe seguir el formato jsonschema
                # Si el schema guardado no es un jsonschema válido, fallará aquí.
                validate(instance=dynamic_data, schema=template.schema)
            except jsonschema.exceptions.ValidationError as e:
                raise serializers.ValidationError({"dynamic_data": f"Error de validación contra el esquema: {e.message}"})
            except Exception as e:
                raise serializers.ValidationError({"dynamic_data": f"Error interno al validar esquema: {str(e)}"})
        
        return data

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

class EmergencyAdmissionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    specialist_name = serializers.CharField(source='specialist_in_charge.user.get_full_name', read_only=True)

    class Meta:
        model = EmergencyAdmission
        fields = '__all__'

class HospitalizationSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    room_name = serializers.CharField(source='bed.room.name', read_only=True)
    bed_name = serializers.CharField(source='bed.name', read_only=True)

    class Meta:
        model = Hospitalization
        fields = '__all__'

class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = '__all__'

class VitalSignsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSigns
        fields = '__all__'

class PrenatalControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrenatalControl
        fields = '__all__'

class NeonatalControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = NeonatalControl
        fields = '__all__'

class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = '__all__'

class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True)
    specialist_name = serializers.CharField(source='specialist.user.get_full_name', read_only=True)

    class Meta:
        model = Prescription
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        prescription = Prescription.objects.create(**validated_data)
        for item_data in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item_data)
        return prescription
