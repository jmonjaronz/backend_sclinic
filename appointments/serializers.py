from rest_framework import serializers
from .models import Appointment, AvailabilityBlock, TreatmentPlan
from clinics.models import Service, Specialist
from patients.models import Patient
from django.db import models
from django.utils import timezone
import datetime

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['id', 'status', 'validated_by', 'validation_date', 'created_at', 'updated_at']

    def validate(self, data):
        # 0. Importar localmente para evitar circular dependencies
        from .services import check_availability
        
        service = data['service']
        date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']
        
        # Obtener clínica (usar la del usuario si no viene en data)
        clinic = data.get('clinic')
        if not clinic:
             request = self.context.get('request')
             if request and hasattr(request.user, 'clinic'):
                 clinic = request.user.clinic
        
        if not clinic:
            raise serializers.ValidationError("Debe especificarse una clínica.")

        specialist = data.get('specialist')
        
        # 1. Ejecutar validación de disponibilidad y capacidad
        is_available, error_message = check_availability(
            clinic=clinic,
            date=date,
            start_time=start_time,
            end_time=end_time,
            specialist=specialist,
            service=service
        )

        if not is_available:
            raise serializers.ValidationError(error_message)

        return data

class TreatmentPlanSerializer(serializers.ModelSerializer):
    sessions_count = serializers.SerializerMethodField()

    class Meta:
        model = TreatmentPlan
        fields = [
            'id', 'clinic', 'patient', 'specialist', 'service', 
            'total_sessions', 'suggested_frequency', 'notes', 
            'total_price', 'is_paid', 'payment_status', 'created_at',
            'sessions_count'
        ]
        read_only_fields = ['id', 'is_paid', 'created_at']

    def get_sessions_count(self, obj):
        return obj.sessions.count()

class AvailabilityBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilityBlock
        fields = '__all__'
