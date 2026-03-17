from rest_framework import permissions
from clinics.models import ClinicModuleSubscription

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'SUPERADMIN')

class IsClinicStaff(permissions.BasePermission):
    """Admin, Psicólogo, Staff de la clínica."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                    request.user.role in ['ADMIN_CLINIC', 'PSYCHOLOGIST', 'STAFF', 'SUPERADMIN'])

class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                    (request.user.role == 'PATIENT' or request.user.role == 'SUPERADMIN'))

class IsCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                    (request.user.role == 'COMPANY' or request.user.role == 'SUPERADMIN'))

class ClinicHasModulePermission(permissions.BasePermission):
    """
    Verifica si la clínica tiene el módulo requerido activo.
    La vista debe definir un atributo `required_module = 'module_name'`.
    """
    def has_permission(self, request, view):
        module_name = getattr(view, 'required_module', None)
        if not module_name:
            return True
            
        clinic = getattr(request, 'clinic', None)
        if not clinic:
            return False 
            
        return ClinicModuleSubscription.objects.filter(
            clinic=clinic,
            module__name=module_name,
            module__is_active_globally=True,
            is_active=True
        ).exists()

class PortalAccessPermission(permissions.BasePermission):
    """
    Controls access based on the target portal.
    Portals: INTRANET, PATIENT, B2B.
    """
    def has_permission(self, request, view):
        portal = getattr(view, 'portal_type', None)
        if not portal:
            return True # Not restricted by portal
            
        user = request.user
        if not user or not user.is_authenticated:
            return False
            
        from users.models import User
        
        if portal == User.PortalType.INTRANET:
            # Must have an active role from the clinic
            return user.active_role is not None and user.active_role.clinic == request.clinic
            
        if portal == User.PortalType.PATIENT:
            return user.role == User.Role.PATIENT
            
        if portal == User.PortalType.B2B:
            return user.role == User.Role.COMPANY
            
        return False
