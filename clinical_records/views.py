from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import (
    ClinicalRecord, SessionNote, EmergencyAdmission, Hospitalization, Treatment, 
    VitalSigns, PrenatalControl, NeonatalControl, Prescription
)
from .serializers import (
    ClinicalRecordSerializer, SessionNoteSerializer,
    EmergencyAdmissionSerializer, HospitalizationSerializer, TreatmentSerializer,
    VitalSignsSerializer, PrenatalControlSerializer, NeonatalControlSerializer,
    PrescriptionSerializer
)
from .services import AutocompleteService, PrescriptionService
from django.db.models import Q
from core.viewsets import BaseViewSet
from core.mixins import ClinicalAuditReadMixin
from users.models import User

class ClinicalRecordViewSet(ClinicalAuditReadMixin, BaseViewSet):
    """
    Gestión de Expedientes Clínicos.
    Los psicólogos solo ven los expedientes a los que están asignados o en los que tienen notas.
    """
    serializer_class = ClinicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_audit_patient_id(self, instance):
        return instance.patient.id if instance.patient else None

    def get_queryset(self):
        user = self.request.user
        # ClinicIsolationMixin already filters by clinic or returns none()
        base_qs = super().get_queryset()
        
        if user.role == User.Role.SPECIALIST or user.role == 'PSYCHOLOGIST': # Support both for safety
            # Ver registros asignados explícitamente O donde el psicólogo escribió una nota
            return base_qs.filter(
                Q(assigned_specialists__user=user) | 
                Q(session_notes__specialist__user=user)
            ).distinct()
            
        elif user.role in [User.Role.ADMIN_CLINIC, User.Role.SUPERADMIN]:
            return base_qs

        # Otros roles (Pacientes, Empresas) no deberían acceder a registros clínicos directos.
        return base_qs.none()

class SessionNoteViewSet(ClinicalAuditReadMixin, BaseViewSet):
    """
    Notas de Sesión o Evoluciones.
    Permite el CRUD básico, sujeto a reglas de inmutabilidad (is_locked).
    """
    serializer_class = SessionNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_audit_patient_id(self, instance):
        return instance.record.patient.id if instance.record and instance.record.patient else None

    def get_queryset(self):
        user = self.request.user
        base_qs = super().get_queryset()

        if user.role == User.Role.SPECIALIST or user.role == 'PSYCHOLOGIST':
            return base_qs.filter(specialist__user=user)
        
        elif user.role in [User.Role.ADMIN_CLINIC, User.Role.SUPERADMIN]:
            return base_qs

        return base_qs.none()

    def perform_destroy(self, instance):
        if instance.is_locked:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("No se puede eliminar una nota de sesión bloqueada.")
        instance.delete()

    def create(self, request, *args, **kwargs):
        # Validación de Triaje Obligatorio (Si la clínica lo requiere)
        record_id = request.data.get('record')
        appointment_id = request.data.get('appointment')
        
        if record_id and appointment_id:
            try:
                record = ClinicalRecord.objects.get(id=record_id)
                if record.clinic.requires_triage_before_appointment:
                    # Verificar si existe registro de Signos Vitales para esta cita
                    if not VitalSigns.objects.filter(appointment_id=appointment_id).exists():
                        from rest_framework.exceptions import ValidationError
                        raise ValidationError(
                            "Esta clínica requiere un triaje (Signos Vitales) previo antes de iniciar la consulta médica."
                        )
            except ClinicalRecord.DoesNotExist:
                from rest_framework.exceptions import ValidationError
                raise ValidationError("El registro clínico especificado no existe.")
        
        return super().create(request, *args, **kwargs)

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

class EmergencyAdmissionViewSet(BaseViewSet):
    queryset = EmergencyAdmission.objects.all()
    serializer_class = EmergencyAdmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

class HospitalizationViewSet(BaseViewSet):
    queryset = Hospitalization.objects.all()
    serializer_class = HospitalizationSerializer
    permission_classes = [permissions.IsAuthenticated]

class TreatmentViewSet(BaseViewSet):
    queryset = Treatment.objects.all()
    serializer_class = TreatmentSerializer
    permission_classes = [permissions.IsAuthenticated]

class VitalSignsViewSet(BaseViewSet):
    queryset = VitalSigns.objects.all()
    serializer_class = VitalSignsSerializer
    permission_classes = [permissions.IsAuthenticated]

class PrenatalControlViewSet(BaseViewSet):
    queryset = PrenatalControl.objects.all()
    serializer_class = PrenatalControlSerializer
    permission_classes = [permissions.IsAuthenticated]

class NeonatalControlViewSet(BaseViewSet):
    queryset = NeonatalControl.objects.all()
    serializer_class = NeonatalControlSerializer
    permission_classes = [permissions.IsAuthenticated]

class PrescriptionViewSet(BaseViewSet):
    """
    Gestión de Recetas Médicas con validación de alergias.
    """
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Validación PROACTIVA de Alergias antes de crear
        patient_id = request.data.get('patient')
        medications = request.data.get('items', []) # Lista de nombres o IDs
        
        if patient_id and medications:
            from patients.models import Patient
            try:
                patient = Patient.objects.get(id=patient_id)
                conflicts = PrescriptionService.check_allergies(patient, medications)
                if conflicts:
                    # Si hay conflictos pero no vienen con override_reason, advertir.
                    if not request.data.get('allergy_override_reason'):
                        return Response({
                            "detail": "Se han detectado posibles alergias.",
                            "conflicts": conflicts,
                            "requires_override": True
                        }, status=status.HTTP_409_CONFLICT)
            except Patient.DoesNotExist:
                pass

        return super().create(request, *args, **kwargs)

class DiagnosisSearchViewSet(viewsets.ViewSet):
    """
    Buscador de diagnósticos CIE-10.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response([])
        
        results = AutocompleteService.search_diagnosis(query)
        return Response(results)
