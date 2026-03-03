from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import PatientRegistrationSerializer

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
