from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import ClinicalRecord, SessionNote
from .serializers import ClinicalRecordSerializer, SessionNoteSerializer
from .permissions import IsAssignedSpecialist

class ClinicalRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing Clinical Records.
    Only assigned specialists or clinic admins can see them.
    """
    queryset = ClinicalRecord.objects.all()
    serializer_class = ClinicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsAssignedSpecialist]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'SUPERADMIN':
            return self.queryset
        
        qs = self.queryset.filter(clinic=user.clinic)
        
        if user.role == 'PSYCHOLOGIST':
            # Filter where the psychologist is explicitly assigned
            if hasattr(user, 'specialist_profile'):
                return qs.filter(assigned_specialists=user.specialist_profile)
        
        if user.role == 'PATIENT':
            # A patient can only see their own record
            if hasattr(user, 'patient_profile'):
                return qs.filter(patient=user.patient_profile)
                
        return qs

class SessionNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Session Notes (evolutions).
    """
    queryset = SessionNote.objects.all()
    serializer_class = SessionNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsAssignedSpecialist]

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset.filter(record__clinic=user.clinic)
        
        if user.role == 'PSYCHOLOGIST' and hasattr(user, 'specialist_profile'):
            # Psychology sees notes they wrote OR notes from records they are assigned to
            from django.db.models import Q
            return qs.filter(
                Q(specialist=user.specialist_profile) | 
                Q(record__assigned_specialists=user.specialist_profile)
            ).distinct()
            
        if user.role == 'PATIENT' and hasattr(user, 'patient_profile'):
            return qs.filter(record__patient=user.patient_profile)

        return qs

    def perform_create(self, serializer):
        # Automatically assign the specialist from the authenticated user
        if hasattr(self.request.user, 'specialist_profile'):
            serializer.save(specialist=self.request.user.specialist_profile)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], url_path='lock')
    def lock_note(self, request, pk=None):
        note = self.get_object()
        if note.is_locked:
            return Response({"error": "La nota ya está bloqueada."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Only the author can lock the note
        if hasattr(request.user, 'specialist_profile') and note.specialist != request.user.specialist_profile:
             return Response({"error": "Solo el autor puede bloquear la nota."}, status=status.HTTP_403_FORBIDDEN)

        note.is_locked = True
        note.locked_at = timezone.now()
        note.save()
        return Response({"message": "Nota bloqueada exitosamente."})

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_locked:
            return Response({"error": "No se puede editar una nota bloqueada."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
