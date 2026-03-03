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
        service = data['service']
        date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']
        clinic = data.get('clinic') or self.context['request'].user.clinic
        specialist = data.get('specialist')
        headquarters = data.get('headquarters')
        modality = data.get('modality', Appointment.Modality.PRESENCIAL)

        from django.utils import timezone
        import datetime

        # Create localized datetimes for comparison
        # Assuming server and data are in the same timezone (America/Lima as per settings)
        start_dt = timezone.make_aware(datetime.datetime.combine(date, start_time))
        end_dt = timezone.make_aware(datetime.datetime.combine(date, end_time))

        # 1. Check for availability blocks (Precise time check)
        # Specialist blocks
        if specialist:
            if AvailabilityBlock.objects.filter(
                clinic=clinic,
                specialist=specialist,
                start_datetime__lt=end_dt,
                end_datetime__gt=start_dt
            ).exists():
                raise serializers.ValidationError(f"El especialista {specialist} no está disponible en este horario (bloqueo detectado).")
            
        # Clinic blocks
        if AvailabilityBlock.objects.filter(
            clinic=clinic,
            specialist__isnull=True,
            start_datetime__lt=end_dt,
            end_datetime__gt=start_dt
        ).exists():
            raise serializers.ValidationError("La clínica tiene un bloqueo general en este horario.")

        # 2. Capacity and Simultaneous bookings logic
        if not service.is_simultaneous:
            # Individual service: Specialist must be free at that exact time
            if specialist:
                conflicting = Appointment.objects.filter(
                    specialist=specialist,
                    date=date,
                    status__in=[Appointment.Status.PENDING_PAYMENT, Appointment.Status.PENDING_VALIDATION, Appointment.Status.CONFIRMED]
                ).filter(
                    models.Q(start_time__lt=end_time, end_time__gt=start_time)
                ).exclude(id=self.instance.id if self.instance else None)
                
                if conflicting.exists():
                    raise serializers.ValidationError("El especialista ya tiene una cita reservada o en validación en este horario.")
        else:
            # Simultaneous service (Group): Check max_capacity
            # The limit applies specifically to PRESENCIAL if it's a physical room
            if modality == Appointment.Modality.PRESENCIAL:
                existing_count = Appointment.objects.filter(
                    clinic=clinic,
                    service=service,
                    date=date,
                    start_time=start_time,
                    modality=Appointment.Modality.PRESENCIAL,
                    status__in=[Appointment.Status.PENDING_PAYMENT, Appointment.Status.PENDING_VALIDATION, Appointment.Status.CONFIRMED]
                ).count()
                
                if existing_count >= service.max_capacity:
                    raise serializers.ValidationError(f"La capacidad máxima presencial para este servicio en este horario se ha agotado ({service.max_capacity} personas).")
            
            # For VIRTUAL, maybe there is no limit or a different one, but user said "ahí hay menos limitación"
            # We follow the same max_capacity just in case, unless specified otherwise.

        return data

class TreatmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentPlan
        fields = '__all__'
        read_only_fields = ['id', 'is_paid', 'created_at']

class AvailabilityBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilityBlock
        fields = '__all__'
