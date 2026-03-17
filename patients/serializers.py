from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from .models import Patient, DependentLink, EmergencyContact, PatientFamilyLink
from core.models import Clinic

User = get_user_model()

class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'phone', 'relationship']

class PatientFamilyLinkSerializer(serializers.ModelSerializer):
    patient_related_name = serializers.CharField(source='patient_related.get_full_name', read_only=True)
    
    class Meta:
        model = PatientFamilyLink
        fields = ['id', 'patient_origin', 'patient_related', 'patient_related_name', 'relationship', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

class PatientRegistrationSerializer(serializers.Serializer):
    # Clinic ID is required for multi-tenancy
    clinic_id = serializers.UUIDField()
    
    # Common fields
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    document_type = serializers.ChoiceField(choices=Patient.DocumentType.choices)
    document_number = serializers.CharField(max_length=50)
    birth_date = serializers.DateField()
    gender = serializers.ChoiceField(choices=Patient.Gender.choices, required=False)
    
    # Location
    department = serializers.CharField(max_length=100, required=False)
    province = serializers.CharField(max_length=100, required=False)
    district = serializers.CharField(max_length=100, required=False)
    address = serializers.CharField(required=False)
    
    # Additional data
    occupation = serializers.CharField(max_length=100, required=False)
    religion = serializers.CharField(max_length=100, required=False)
    company = serializers.CharField(max_length=100, required=False, default='Otro')
    native_language = serializers.CharField(max_length=100, required=False)
    academic_degree = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=20, required=False)
    email = serializers.EmailField(required=True)
    civil_status = serializers.ChoiceField(choices=Patient.CivilStatus.choices, required=False)
    
    # Specific for minors/dependents
    is_minor = serializers.BooleanField(default=False)
    educational_institution = serializers.CharField(max_length=100, required=False)
    grade_section = serializers.CharField(max_length=100, required=False)
    
    # Tutor info (if it's a minor or if registered by third party)
    tutor_id = serializers.IntegerField(required=False, allow_null=True)
    relationship = serializers.ChoiceField(choices=DependentLink.Relationship.choices, required=False)
    
    # Emergency Contact
    emergency_contact = EmergencyContactSerializer(required=False)
    
    # Registration type (Self-registration vs Staff-led)
    is_staff_led = serializers.BooleanField(default=False)
    password = serializers.CharField(write_only=True, required=False)
    terms_accepted = serializers.BooleanField()

    def validate(self, data):
        if not data.get('terms_accepted'):
            raise serializers.ValidationError("Debe aceptar los términos y condiciones.")
        
        # Check if patient already exists in this clinic
        if Patient.objects.filter(
            clinic_id=data['clinic_id'],
            document_type=data['document_type'],
            document_number=data['document_number']
        ).exists():
            raise serializers.ValidationError("Un paciente con este documento ya está registrado en esta clínica.")

        from datetime import date
        today = date.today()
        birth_date = data.get('birth_date')
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        tutor_id = data.get('tutor_id')
        is_staff_led = data.get('is_staff_led', False)

        # 1. Public Self-Registration (no tutor provided initially)
        if not tutor_id and not is_staff_led:
            if age < 18:
                raise serializers.ValidationError("Los menores de edad no pueden registrarse directamente. Debe hacerlo su padre, madre o tutor legal desde su propia cuenta.")
        
        # 2. Registering a dependent (tutor provided)
        if tutor_id:
            # Relationship is required if a tutor is provided (minor/disabled adult)
            if not data.get('relationship'):
                raise serializers.ValidationError("Debe indicar el parentesco con el tutor legal.")
                
        return data

    @transaction.atomic
    def create(self, validated_data):
        clinic = Clinic.objects.get(id=validated_data.pop('clinic_id'))
        is_staff_led = validated_data.pop('is_staff_led')
        emergency_data = validated_data.pop('emergency_contact', None)
        tutor_id = validated_data.pop('tutor_id', None)
        relationship = validated_data.pop('relationship', None)
        password = validated_data.pop('password', None)
        
        # 1. Create User account only if 18+ and NOT a minor/dependent who doesn't need personal access
        # The user says "si bien no tienen cuenta el registro lo hace una persona mayor" for dependents.
        # But adults (titular) DO have a count.
        
        is_minor = validated_data.get('is_minor')
        birth_date = validated_data.get('birth_date')
        from datetime import date
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        user = None
        # Only create a user account for independent adults
        if age >= 18 and not is_minor:
            email = validated_data.get('email')
            # Username is doc_type + doc_number
            username = f"{validated_data['document_type']}_{validated_data['document_number']}"
            
            # Check if user already exists
            user = User.objects.filter(username=username).first()
            if not user:
                # Use random password if staff-led
                if is_staff_led and not password:
                    password = get_random_string(12)
                    # TODO: Trigger email here
                    print(f"DEBUG: Contraseña temporal para {email}: {password}")
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=validated_data['first_name'],
                    last_name=validated_data['last_name'],
                    clinic=clinic,
                    role='PATIENT',
                    document_type=validated_data['document_type'],
                    document_number=validated_data['document_number']
                )
                if password:
                    user.set_password(password)
                    user.save()

        # 2. Create Patient profile
        patient = Patient.objects.create(
            clinic=clinic,
            user=user,
            **validated_data
        )

        # 3. Handle Emergency Contact
        if emergency_data:
            EmergencyContact.objects.create(patient=patient, **emergency_data)

        # 4. Handle Tutor Link if minor/dependent
        # If is_minor or if tutor_id is provided (for disabled adults)
        if tutor_id and relationship:
            tutor = User.objects.get(id=tutor_id)
            DependentLink.objects.create(
                tutor=tutor,
                patient=patient,
                relationship=relationship
            )

        return patient

class PatientSerializer(serializers.ModelSerializer):
    emergency_contacts = EmergencyContactSerializer(many=True, required=False)
    tutor_links = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    family_links = PatientFamilyLinkSerializer(source='family_links_sent', many=True, read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'clinic', 'first_name', 'last_name', 'document_type', 
            'document_number', 'birth_date', 'gender', 'department', 'province', 
            'district', 'address', 'occupation', 'religion', 'company', 
            'native_language', 'academic_degree', 'phone', 'email', 'civil_status', 
            'is_minor', 'educational_institution', 'grade_section', 
            'terms_accepted', 'dependent_doc_signed', 'is_validated', 'emergency_contacts',
            'tutor_links', 'family_links'
        ]
        read_only_fields = ['is_validated']
