from rest_framework import viewsets, permissions
from .mixins import ClinicIsolationMixin

class BaseViewSet(ClinicIsolationMixin, viewsets.ModelViewSet):
    """
    ViewSet Base obligatorio para todos los endpoints de la API.
    Centraliza:
    1. Aislamiento Multi-Tenant (vía ClinicIsolationMixin).
    2. Permisos base.
    3. Validación de contexto de clínica.
    """
    permission_classes = [permissions.IsAuthenticated]

class BaseReadOnlyViewSet(ClinicIsolationMixin, viewsets.ReadOnlyModelViewSet):
    """
    Versión de solo lectura del ViewSet Base.
    """
    permission_classes = [permissions.IsAuthenticated]
