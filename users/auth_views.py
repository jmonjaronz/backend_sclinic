from rest_framework import serializers, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    document_type = serializers.CharField(required=True)
    document_number = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    clinic_id = serializers.UUIDField(required=False)
    portal = serializers.ChoiceField(choices=['intranet', 'patient', 'company'], required=False)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                document_type=serializer.validated_data['document_type'],
                document_number=serializer.validated_data['document_number'],
                password=serializer.validated_data['password'],
                clinic_id=serializer.validated_data.get('clinic_id')
            )
            
            if user:
                # Validar acceso al portal solicitado
                portal = serializer.validated_data.get('portal')
                if portal:
                    role_map = {
                        'intranet': ['ADMIN_CLINIC', 'PSYCHOLOGIST', 'STAFF', 'SUPERADMIN'],
                        'patient': ['PATIENT', 'SUPERADMIN'],
                        'company': ['COMPANY', 'SUPERADMIN']
                    }
                    if user.role not in role_map.get(portal, []):
                        return Response({"error": f"Tu rol ({user.role}) no tiene permitido el acceso al portal {portal}."}, status=status.HTTP_403_FORBIDDEN)

                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'clinic_id': user.clinic.id if user.clinic else None
                    }
                })
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['document_type', 'document_number', 'email', 'first_name', 'last_name', 'password', 'role', 'clinic']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get('document_number', validated_data.get('email', '')), 
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            document_type=validated_data.get('document_type', ''),
            document_number=validated_data.get('document_number', ''),
            clinic=validated_data.get('clinic'),
            role=validated_data.get('role', 'PATIENT'),
            password=validated_data['password']
        )
        return user

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuario registrado exitosamente"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
