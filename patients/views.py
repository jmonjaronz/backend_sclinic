from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from .models import Patient
from .serializers import PatientRegistrationSerializer, PatientSerializer

class PatientRegistrationView(APIView):
    """
    Handles registration for both Adults and Minors/Dependents.
    Permissions:
    - If self-registering: AllowAny.
    - If staff-led: IsAuthenticated + Check for STAFF/ADMIN role (TBD).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PatientRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save()
            return Response({
                "message": "Paciente registrado exitosamente.",
                "patient_id": patient.id,
                "document_number": patient.document_number
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientViewSet(viewsets.ModelViewSet):
    """
    Gestión de perfiles de pacientes.
    - Especialistas y Admins ven a todos los de su clínica.
    - Pacientes (Titulares) solo ven sus propios datos y los de sus dependientes.
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Base query to all patients
        base_qs = Patient.objects.all()

        # Isolate by clinic
        if hasattr(user, 'clinic') and user.clinic:
            base_qs = base_qs.filter(clinic=user.clinic)

        if user.role == 'PATIENT':
            # Ver su propio perfil
            own_profile = base_qs.filter(user=user)
            # Ver perfiles de sus dependientes directos en la relación DependentLink
            dependents = base_qs.filter(tutor_links__tutor=user)
            return own_profile | dependents

        # Los demás roles ven todo de su clínica
        return base_qs

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def validate_consent(self, request, pk=None):
        """
        Permite al personal administrativo subir el documento firmado y validar al paciente.
        """
        patient = self.get_object()
        user = request.user
        
        # Solo personal autorizado puede validar
        if user.role not in ['ADMIN_CLINIC', 'STAFF', 'SUPERADMIN']:
            return Response({"detail": "No tiene permiso para validar pacientes."}, status=status.HTTP_403_FOR_CONTENT)
            
        document = request.FILES.get('dependent_doc_signed')
        if not document:
            return Response({"detail": "Debe subir el documento firmado."}, status=status.HTTP_400_BAD_REQUEST)
            
        patient.dependent_doc_signed = document
        patient.is_validated = True
        patient.validated_by = user
        from django.utils import timezone
        patient.validation_date = timezone.now()
        patient.save()
        
        return Response({"message": "Paciente validado exitosamente."}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Bloquear la creación directa en el ViewSet si se requiere
        pasar por nuestro serializador de negocio y vistas dedicadas.
        """
        return Response(
            {"detail": "Use el endpoint POST /api/patients/register/ para crear un paciente nuevo."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
