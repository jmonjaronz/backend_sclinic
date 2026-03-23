from rest_framework import viewsets, permissions
from .mixins import ClinicIsolationMixin
from .permissions import HasCapabilityPermission, PortalAccessPermission

class BaseViewSet(ClinicIsolationMixin, viewsets.ModelViewSet):
    """
    ViewSet Base obligatorio para todos los endpoints de la API.
    Centraliza:
    1. Aislamiento Multi-Tenant (vía ClinicIsolationMixin).
    2. Permisos base (Logeo y ABAC/RBAC).
    3. Validación de contexto de clínica.
    """
    permission_classes = [permissions.IsAuthenticated, PortalAccessPermission, HasCapabilityPermission]

class BaseReadOnlyViewSet(ClinicIsolationMixin, viewsets.ReadOnlyModelViewSet):
    """
    Versión de solo lectura del ViewSet Base con ABAC/RBAC.
    """
    permission_classes = [permissions.IsAuthenticated, PortalAccessPermission, HasCapabilityPermission]

