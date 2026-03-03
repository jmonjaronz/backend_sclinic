from rest_framework import serializers
from .models import ClinicalRecord, SessionNote
from clinics.serializers import SpecialistSerializer

class SessionNoteSerializer(serializers.ModelSerializer):
    specialist_detail = SpecialistSerializer(source='specialist', read_only=True)
    
    class Meta:
        model = SessionNote
        fields = [
            'id', 'record', 'appointment', 'specialist', 'specialist_detail',
            'date', 'session_reason', 'observations', 'diagnosis',
            'therapeutic_objective', 'recommendations', 'commitments',
            'assigned_materials', 'next_session_indications', 'is_locked', 'locked_at'
        ]
        read_only_fields = ['id', 'date', 'is_locked', 'locked_at']

    def validate(self, data):
        # Once a note is locked, it shouldn't be edited. 
        # (This check would usually go in perform_update in the viewset, 
        # but we can add some logic here if needed)
        return data

class ClinicalRecordSerializer(serializers.ModelSerializer):
    session_notes = SessionNoteSerializer(many=True, read_only=True)
    
    class Meta:
        model = ClinicalRecord
        fields = ['id', 'clinic', 'patient', 'session_notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
