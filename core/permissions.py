from rest_framework import permissions

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
