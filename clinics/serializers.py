from rest_framework import serializers
from .models import Clinic, Headquarters, Specialty, Service, Specialist

class HeadquartersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Headquarters
        fields = '__all__'

class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class SpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = '__all__'

class ClinicSerializer(serializers.ModelSerializer):
    headquarters = HeadquartersSerializer(many=True, read_only=True)
    specialties = SpecialtySerializer(many=True, read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Clinic
        fields = ['id', 'name', 'subdomain', 'is_active', 'headquarters', 'specialties', 'services']
