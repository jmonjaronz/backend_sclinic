from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import ClinicalRecord, SessionNote
from .serializers import ClinicalRecordSerializer, SessionNoteSerializer
from django.db.models import Q

class ClinicalRecordViewSet(viewsets.ModelViewSet):
    """
    Gestión de Expedientes Clínicos.
    Los psicólogos solo ven los expedientes a los que están asignados o en los que tienen notas.
    """
    serializer_class = ClinicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_qs = ClinicalRecord.objects.all()
        
        if hasattr(user, 'clinic') and user.clinic:
            base_qs = base_qs.filter(clinic=user.clinic)

        if user.role == 'PSYCHOLOGIST':
            # Ver registros asignados explícitamente O donde el psicólogo escribió una nota
            return base_qs.filter(
                Q(assigned_specialists__user=user) | 
                Q(session_notes__specialist__user=user)
            ).distinct()
            
        elif user.role in ['ADMIN_CLINIC', 'SUPERADMIN']:
            return base_qs

        # Otros roles (Pacientes, Empresas) no deberían acceder a registros clínicos directos.
        return ClinicalRecord.objects.none()

class SessionNoteViewSet(viewsets.ModelViewSet):
    """
    Notas de Sesión o Evoluciones.
    Permite el CRUD básico, sujeto a reglas de inmutabilidad (is_locked).
    """
    serializer_class = SessionNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_qs = SessionNote.objects.all()

        if hasattr(user, 'clinic') and user.clinic:
            base_qs = base_qs.filter(record__clinic=user.clinic)

        if user.role == 'PSYCHOLOGIST':
            return base_qs.filter(specialist__user=user)
        
        elif user.role in ['ADMIN_CLINIC', 'SUPERADMIN']:
            return base_qs

        return SessionNote.objects.none()

    def perform_destroy(self, instance):
        if instance.is_locked:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("No se puede eliminar una nota de sesión bloqueada.")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def lock(self, request, pk=None):
        """
        Bloquea (firma) definitivamente una nota de sesión.
        """
        note = self.get_object()
        
        # Permitir bloquear solo al autor original o al Admin
        if request.user.role == 'PSYCHOLOGIST' and note.specialist.user != request.user:
            return Response(
                {"detail": "Solo el autor puede bloquear (firmar) esta nota."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if note.is_locked:
            return Response(
                {"detail": "Esta nota ya se encuentra bloqueada."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        note.is_locked = True
        note.locked_at = timezone.now()
        note.save(update_fields=['is_locked', 'locked_at'])

        serializer = self.get_serializer(note)
        return Response(serializer.data, status=status.HTTP_200_OK)
