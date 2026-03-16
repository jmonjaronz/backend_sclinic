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
