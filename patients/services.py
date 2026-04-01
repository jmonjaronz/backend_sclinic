#patients/services.py
from .models import Patient, PatientFamilyLink, DependentLink

class PatientPrivacyService:
    """
    Validates if a user or patient has permission to view another patient's data.
    Req: 2_Usuarios_Permisos.md & 3_Pacientes.md
    """
    
    @staticmethod
    def can_access_patient_data(request_user, target_patient_id):
        """
        Main entry point for checking permissions.
        """
        try:
            target_patient = Patient.objects.get(id=target_patient_id)
        except Patient.DoesNotExist:
            return False, "Paciente no encontrado."

        # 1. Own data
        if hasattr(request_user, 'patient_profile') and request_user.patient_profile == target_patient:
            return True, "Acceso permitido a datos propios."

        # 2. Staff/Specialist access (Handled by ViewSet permissions usually, 
        # but here we could add clinic-specific logic)
        if request_user.role in ['SPECIALIST', 'ADMIN_CLINIC', 'SUPERADMIN']:
            # Check if specialist is in the same clinic
            if request_user.clinic == target_patient.clinic:
                return True, "Acceso permitido por rol profesional."

        # 3. Family/Dependent access (Patient Portal)
        # Check if the user is a tutor of the patient
        is_tutor = DependentLink.objects.filter(
            tutor=request_user, 
            patient=target_patient, 
            is_validated=True
        ).exists()
        
        if is_tutor:
            return True, "Acceso permitido como tutor validado."

        # 4. Family links (Patient to Patient)
        if hasattr(request_user, 'patient_profile'):
            user_patient = request_user.patient_profile
            # Check for active family links that allow viewing (e.g. Parent seeing Child)
            # This could be more granular based on RelationshipType
            is_family = PatientFamilyLink.objects.filter(
                patient_origin=user_patient,
                patient_related=target_patient,
                status='ACTIVE'
            ).exists()
            
            if is_family:
                return True, "Acceso permitido por vínculo familiar activo."

        return False, "No tiene permisos para acceder a este registro clínico."
