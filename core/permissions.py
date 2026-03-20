from rest_framework import permissions
from users.models import User
from core.utils.tenant_utils import has_feature

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.SUPERADMIN)

class IsClinicStaff(permissions.BasePermission):
    """Admin, Psicólogo, Staff de la clínica."""
    def has_permission(self, request, view):
        if not getattr(request, 'clinic', None):
            return False
        return bool(request.user and request.user.is_authenticated and 
                    request.user.role in [User.Role.ADMIN_CLINIC, User.Role.SPECIALIST, User.Role.STAFF, User.Role.SUPERADMIN])

class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                    (request.user.role == User.Role.PATIENT or request.user.role == User.Role.SUPERADMIN))

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
        return has_feature(clinic, module_name)

class PortalAccessPermission(permissions.BasePermission):
    """
    Controls access based on the target portal.
    Portals: INTRANET, PATIENT, B2B.
    """
    def has_permission(self, request, view):
        portal = getattr(view, 'portal_type', None)
        if not portal:
            return True # Not restricted by portal
            
        clinic = getattr(request, 'clinic', None)
        if not clinic:
            return False

        user = request.user
        if not user or not user.is_authenticated:
            return False
            
        if portal == User.PortalType.INTRANET:
            # Must have an active role from the clinic
            return user.active_role is not None and user.active_role.clinic == clinic
            
        if portal == User.Role.PATIENT:
            return user.role == User.Role.PATIENT
            
        if portal == User.Role.COMPANY:
            return user.role == User.Role.COMPANY
            
        return False
