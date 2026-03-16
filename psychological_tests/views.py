from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import models
from django.utils import timezone
from .models import (
    PsychologicalTest, TestApplication, TestBattery,
    Answer, Question, ScaleOption, Baremo, Dimension
)
from .serializers import (
    PsychologicalTestSerializer, TestApplicationSerializer,
    TestBatterySerializer, DimensionSerializer, BaremoSerializer
)
from .logic import calculate_test_results


class TestBatteryViewSet(viewsets.ModelViewSet):
    serializer_class = TestBatterySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        clinic = getattr(self.request.user, 'clinic', None)
        if clinic:
            return TestBattery.objects.filter(clinic=clinic)
        return TestBattery.objects.none()

    def perform_create(self, serializer):
        serializer.save(clinic=self.request.user.clinic)


class PsychologicalTestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Catálogo de Tests Psicológicos disponibles.
    """
    queryset = PsychologicalTest.objects.all()
    serializer_class = PsychologicalTestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        clinic = getattr(self.request.user, 'clinic', None)
        return PsychologicalTest.objects.filter(
            models.Q(clinic=clinic) | models.Q(clinic__isnull=True)
        )


class TestApplicationViewSet(viewsets.ModelViewSet):
    """
    Gestión de Aplicaciones de Tests.
    """
    serializer_class = TestApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        clinic = getattr(user, 'clinic', None)
        base_qs = TestApplication.objects.filter(clinic=clinic)

        if user.role == 'PATIENT':
            return base_qs.filter(patient__user=user).exclude(
                appointment__service__is_confidential_to_patient=True
            )

        if hasattr(user, 'managed_company'):
            # Empresas solo ven tests vinculados a su compañía
            return base_qs.filter(appointment__company=user.managed_company)

        # Especialista/Admin ve todos los de su clínica
        return base_qs

    def perform_create(self, serializer):
        clinic = getattr(self.request.user, 'clinic', None)
        serializer.save(clinic=clinic)

    @action(detail=False, methods=['get'])
    def my_pending(self, request):
        """
        Lista los tests asignados al paciente autenticado que aún no ha completado.
        """
        user = request.user
        if user.role != 'PATIENT':
            return Response(
                {'detail': 'Solo los pacientes pueden usar este endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )

        pending = TestApplication.objects.filter(
            patient__user=user,
            completed_at__isnull=True
        ).exclude(appointment__service__is_confidential_to_patient=True)

        serializer = TestApplicationSerializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit_answers(self, request, pk=None):
        """
        El paciente envía sus respuestas a un test asignado.
        Dispara el cálculo automático de puntajes y baremos.

        Body: { "answers": [{"question_id": <int>, "option_id": <int>}, ...] }
        """
        application = self.get_object()
        user = request.user

        # Solo el paciente dueño puede responder
        if user.role == 'PATIENT' and application.patient.user != user:
            return Response(
                {'error': 'No tienes permiso para responder este test.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if application.completed_at:
            return Response(
                {'error': 'Este test ya fue completado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if application.valid_until and timezone.now() > application.valid_until:
            return Response(
                {'error': 'El plazo para responder este test ha expirado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        answers_data = request.data.get('answers', [])
        if not answers_data:
            return Response(
                {'error': 'Debe enviar al menos una respuesta.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Borrar respuestas anteriores en caso de reintento parcial
        application.answers.all().delete()

        errors = []
        for item in answers_data:
            q_id = item.get('question_id')
            opt_id = item.get('option_id')
            try:
                question = Question.objects.get(id=q_id, dimension__test=application.test)
                option = ScaleOption.objects.get(id=opt_id, test=application.test)
                Answer.objects.create(
                    application=application,
                    question=question,
                    selected_option=option
                )
            except (Question.DoesNotExist, ScaleOption.DoesNotExist):
                errors.append({'question_id': q_id, 'error': 'Pregunta u opción inválida.'})

        if errors:
            application.answers.all().delete()
            return Response(
                {'error': 'Algunas respuestas son inválidas.', 'details': errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Disparar calificación automática
        result = calculate_test_results(application.id)
        serializer = TestApplicationSerializer(result)
        return Response({
            'message': 'Test completado y calificado exitosamente.',
            'result': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def add_clinical_notes(self, request, pk=None):
        """
        El psicólogo añade / actualiza sus observaciones clínicas sobre los resultados.
        Body: { "clinical_notes": "..." }
        """
        application = self.get_object()
        user = request.user

        if user.role not in ['PSYCHOLOGIST', 'ADMIN_CLINIC', 'SUPERADMIN']:
            return Response(
                {'error': 'Solo especialistas pueden agregar notas clínicas.'},
                status=status.HTTP_403_FORBIDDEN
            )

        notes = request.data.get('clinical_notes', '').strip()
        if not notes:
            return Response(
                {'error': 'Las notas clínicas no pueden estar vacías.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        application.clinical_notes = notes
        application.save(update_fields=['clinical_notes'])
        return Response({'message': 'Notas clínicas guardadas.', 'clinical_notes': notes})


# ─── Admin ViewSets (configuración del catálogo desde la Intranet) ───

class DimensionViewSet(viewsets.ModelViewSet):
    """CRUD de dimensiones de un test."""
    serializer_class = DimensionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        clinic = getattr(self.request.user, 'clinic', None)
        return Dimension.objects.filter(test__clinic=clinic)


class BaremoViewSet(viewsets.ModelViewSet):
    """CRUD de baremos/escalas de interpretación."""
    serializer_class = BaremoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        clinic = getattr(self.request.user, 'clinic', None)
        return Baremo.objects.filter(
            models.Q(clinic=clinic) | models.Q(clinic__isnull=True)
        )
