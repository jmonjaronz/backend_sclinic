from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    Gestión de notificaciones del usuario autenticado.
    - GET  /notifications/          → listar las propias (paginado)
    - GET  /notifications/{id}/     → detalle
    - POST /notifications/{id}/read/  → marcar como leída
    - POST /notifications/read_all/   → marcar todas como leídas
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        """Marca una notificación específica como leída."""
        notif = self.get_object()
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        return Response({'message': 'Notificación marcada como leída.'})

    @action(detail=False, methods=['post'])
    def read_all(self, request):
        """Marca todas las notificaciones no leídas del usuario como leídas."""
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        return Response({'message': f'{count} notificaciones marcadas como leídas.'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Retorna el número de notificaciones no leídas (para el badge del frontend)."""
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})
