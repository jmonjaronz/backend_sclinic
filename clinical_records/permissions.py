from rest_framework import permissions

class IsAssignedSpecialist(permissions.BasePermission):
    """
    Allows access only to:
    - Admin/SuperAdmin
    - Specialists explicitly assigned to the clinical record.
    - Author of a specific session note.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # SuperAdmin and Admins have full access
        if request.user.role in ['SUPERADMIN', 'ADMIN_CLINIC']:
            return True
        
        # Specialists and Patients (Titular) might have some access
        return request.user.role in ['PSYCHOLOGIST', 'PATIENT']

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if user.role in ['SUPERADMIN', 'ADMIN_CLINIC']:
            return True

        from .models import ClinicalRecord, SessionNote
        
        # 1. Access to the ClinicalRecord itself
        if isinstance(obj, ClinicalRecord):
            # Check if specialist is in assigned_specialists
            if hasattr(user, 'specialist_profile'):
                return obj.assigned_specialists.filter(id=user.specialist_profile.id).exists()
            # If patient, they can only see their own record
            if hasattr(user, 'patient_profile'):
                return obj.patient == user.patient_profile
            return False

        # 2. Access to a SessionNote
        if isinstance(obj, SessionNote):
            # Specialist author always has access
            if hasattr(user, 'specialist_profile') and obj.specialist == user.specialist_profile:
                return True
            # Other assigned specialists might see it too
            if hasattr(user, 'specialist_profile'):
                 return obj.record.assigned_specialists.filter(id=user.specialist_profile.id).exists()
            # Patient can see their own session notes
            if hasattr(user, 'patient_profile'):
                return obj.record.patient == user.patient_profile
            return False

        return False
