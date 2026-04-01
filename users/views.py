#users/views.py
"""
Views para gestión RBAC dinámica del sistema SCLINIC.
Req: 2_Usuarios_Permisos.md – Roles Dinámicos, Capabilities y UserRole.
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from core.viewsets import BaseViewSet, BaseReadOnlyViewSet
from core.models.tenant import get_current_clinic
from .models import Capability, RoleTemplate, DynamicRole, UserRole
from .serializers import (
    CapabilitySerializer,
    RoleTemplateSerializer,
    DynamicRoleSerializer,
    DynamicRoleCloneSerializer,
    UserRoleSerializer,
    SwitchActiveRoleSerializer,
)
from .auth_views import RegisterView, LoginView  # re-exportar para urls


# ─────────────────── Capability (read-only) ──────────────────────────────────

class CapabilityViewSet(BaseReadOnlyViewSet):
    """
    Lista todas las capabilities disponibles en el sistema.
    Solo lectura. Filtrado por módulo opcional: ?module=patient
    """
    queryset = Capability.objects.all()
    serializer_class = CapabilitySerializer
    required_capabilities = {
        'list': 'admin.roles.manage',
        'retrieve': 'admin.roles.manage',
    }

    def get_queryset(self):
        qs = Capability.objects.all()
        module = self.request.query_params.get('module')
        if module:
            qs = qs.filter(module=module)
        return qs


# ─────────────────── RoleTemplate (read-only) ────────────────────────────────

class RoleTemplateViewSet(BaseReadOnlyViewSet):
    """
    Lista las plantillas de roles base del sistema.
    Permite clonar una plantilla como DynamicRole para la clínica activa.
    """
    queryset = RoleTemplate.objects.all()
    serializer_class = RoleTemplateSerializer
    required_capabilities = {
        'list': 'admin.roles.manage',
        'retrieve': 'admin.roles.manage',
    }

    @action(detail=True, methods=['post'], url_path='clone')
    def clone(self, request, pk=None):
        """
        POST /api/role-templates/{id}/clone/
        Clona esta plantilla como un DynamicRole para la clínica activa.
        """
        template = self.get_object()
        clinic = get_current_clinic()
        if not clinic:
            return Response({'detail': 'Contexto de clínica requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DynamicRoleCloneSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data.get('name') or template.name

        # Crear el DynamicRole con las capabilities de la plantilla
        role, created = DynamicRole.objects.get_or_create(
            clinic=clinic,
            name=name,
            defaults={'is_active': True},
        )
        if created:
            role.capabilities.set(template.capabilities.all())
        
        return Response(
            DynamicRoleSerializer(role).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


# ─────────────────── DynamicRole (CRUD) ──────────────────────────────────────

class DynamicRoleViewSet(BaseViewSet):
    """
    CRUD de roles dinámicos para la clínica activa.
    Req: 2_Usuarios_Permisos.md sec. 2.2 – Roles por clínica.
    """
    serializer_class = DynamicRoleSerializer
    required_capabilities = {
        'list': 'admin.roles.manage',
        'retrieve': 'admin.roles.manage',
        'create': 'admin.roles.manage',
        'update': 'admin.roles.manage',
        'partial_update': 'admin.roles.manage',
        'destroy': 'admin.roles.manage',
    }

    def get_queryset(self):
        clinic = get_current_clinic()
        if not clinic:
            return DynamicRole.objects.none()
        return DynamicRole.objects.filter(clinic=clinic).prefetch_related('capabilities')

    def perform_create(self, serializer):
        clinic = get_current_clinic()
        if not clinic:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Se requiere contexto de clínica.')
        serializer.save(clinic=clinic)


# ─────────────────── UserRole (Asignación de roles a usuarios) ───────────────

class UserRoleViewSet(BaseViewSet):
    """
    Gestión de la asignación de roles dinámicos a usuarios.
    Permite asignar y revocar roles dentro de la clínica activa.
    """
    serializer_class = UserRoleSerializer
    required_capabilities = {
        'list': 'admin.users.manage',
        'retrieve': 'admin.users.manage',
        'create': 'admin.users.manage',
        'destroy': 'admin.users.manage',
        'update': 'admin.users.manage',
        'partial_update': 'admin.users.manage',
    }

    def get_queryset(self):
        clinic = get_current_clinic()
        if not clinic:
            return UserRole.objects.none()
        return UserRole.objects.filter(role__clinic=clinic).select_related('user', 'role')


# ─────────────────── Switch Active Role ──────────────────────────────────────

class SwitchActiveRoleView(APIView):
    """
    POST /api/users/me/switch-role/
    Cambia el rol activo del usuario autenticado.
    Req: 2_Usuarios_Permisos.md sec. 2.2 – Seleccionar rol activo en login.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SwitchActiveRoleSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data['role_id']
        success = request.user.switch_active_role(role)

        if success:
            return Response({'detail': f'Rol activo cambiado a: {role.name}'}, status=status.HTTP_200_OK)
        return Response({'detail': 'No tienes acceso a ese rol.'}, status=status.HTTP_403_FORBIDDEN)
