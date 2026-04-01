#users/serializers.py
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Capability, RoleTemplate, DynamicRole, UserRole


# ─────────────────── UserSerializer (existente) ───────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'active_role', 'clinic', 'document_type', 'document_number', 'password',
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# ─────────────────── Auth / JWT Overrides ─────────────────────────────────────

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Sobrescribe el serializador por defecto de SimpleJWT para incluir claims
    específicos del sistema multi-tenant y multi-contexto.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Inyectar claims fijos de BD
        token['clinic_id'] = str(user.clinic.id) if user.clinic else None
        token['roles'] = user.role
        token['active_role_id'] = str(user.active_role.id) if user.active_role else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # El context y request están disponibles en self.context cuando se usa la vista correcta.
        request = self.context.get('request')
        
        import jwt
        # Necesitamos volver a firmar el token con el X-App-Context si existe
        app_context = getattr(request, 'app_context', None)
        if app_context:
            refresh = self.get_token(self.user)
            refresh['app_context'] = app_context
            
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            
        return data


# ─────────────────── Capability ───────────────────────────────────────────────

class CapabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Capability
        fields = ['id', 'codename', 'description', 'module']
        read_only_fields = ['id']


# ─────────────────── RoleTemplate ─────────────────────────────────────────────

class RoleTemplateSerializer(serializers.ModelSerializer):
    capabilities = CapabilitySerializer(many=True, read_only=True)

    class Meta:
        model = RoleTemplate
        fields = ['id', 'name', 'description', 'capabilities']
        read_only_fields = ['id']


# ─────────────────── DynamicRole ──────────────────────────────────────────────

class DynamicRoleSerializer(serializers.ModelSerializer):
    capabilities = CapabilitySerializer(many=True, read_only=True)
    capability_ids = serializers.PrimaryKeyRelatedField(
        queryset=Capability.objects.all(), many=True, write_only=True, source='capabilities'
    )

    class Meta:
        model = DynamicRole
        fields = ['id', 'clinic', 'name', 'capabilities', 'capability_ids', 'is_active']
        read_only_fields = ['id', 'clinic', 'capabilities']

    def validate_capability_ids(self, value):
        """Req: 2_Usuarios_Permisos.md sec. 2.3 – Un rol debe tener al menos un permiso."""
        if not value:
            raise serializers.ValidationError("El rol debe tener al menos un permiso asignado.")
        return value

    def create(self, validated_data):
        capabilities = validated_data.pop('capabilities', [])
        role = DynamicRole.objects.create(**validated_data)
        role.capabilities.set(capabilities)
        return role

    def update(self, instance, validated_data):
        capabilities = validated_data.pop('capabilities', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if capabilities is not None:
            if not capabilities:
                raise serializers.ValidationError({"capability_ids": "El rol debe tener al menos un permiso asignado."})
            instance.capabilities.set(capabilities)
        return instance


class DynamicRoleCloneSerializer(serializers.Serializer):
    """Clona un RoleTemplate como un DynamicRole para la clínica activa."""
    template_id = serializers.PrimaryKeyRelatedField(queryset=RoleTemplate.objects.all())
    name = serializers.CharField(max_length=100, required=False, help_text="Nombre personalizado. Por defecto: nombre de la plantilla.")

    def validate_name(self, value):
        return value.strip() if value else value


# ─────────────────── UserRole ─────────────────────────────────────────────────

class UserRoleSerializer(serializers.ModelSerializer):
    role_detail = DynamicRoleSerializer(source='role', read_only=True)

    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role', 'role_detail', 'is_primary', 'assigned_at']
        read_only_fields = ['id', 'assigned_at', 'role_detail']


# ─────────────────── Switch Active Role ───────────────────────────────────────

class SwitchActiveRoleSerializer(serializers.Serializer):
    role_id = serializers.PrimaryKeyRelatedField(queryset=DynamicRole.objects.all())

    def validate_role_id(self, role):
        request = self.context.get('request')
        if request:
            # Verificar que el rol pertenece a la clínica del usuario
            user = request.user
            if not user.dynamic_roles.filter(role=role).exists():
                raise serializers.ValidationError("No tienes acceso a este rol.")
        return role

