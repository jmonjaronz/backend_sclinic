from rest_framework import viewsets, permissions
from core.models import Clinic
from .models import (
    Headquarters, Service, Specialist, SubscriptionPlan, Subscription, 
    Room, Bed, SpecialistSchedule, DynamicBrandingEngine
)
from .serializers import (
    ClinicSerializer, HeadquartersSerializer,
    ServiceSerializer, SpecialistSerializer, SubscriptionPlanSerializer,
    SubscriptionSerializer, RoomSerializer, BedSerializer, 
    SpecialistScheduleSerializer, DynamicBrandingSerializer
)
from core.permissions import IsSuperAdmin
from core.mixins import ClinicIsolationMixin
from users.models import User

class PublicClinicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public access to clinic data.
    """
    queryset = Clinic.objects.filter(status=Clinic.Status.ACTIVE)
    serializer_class = ClinicSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'subdomain'

class AdminClinicViewSet(viewsets.ModelViewSet):
    """
    SuperAdmin management of all clinics.
    """
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [IsSuperAdmin]

class PublicHeadquartersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Headquarters.objects.all()
    serializer_class = HeadquartersSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        clinic_id = self.request.query_params.get('clinic')
        if clinic_id:
            return self.queryset.filter(clinic_id=clinic_id)
        return self.queryset.none()

class PublicServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        clinic_id = self.request.query_params.get('clinic')
        if clinic_id:
            return self.queryset.filter(clinic_id=clinic_id)
        return self.queryset.none()

class PublicSpecialistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialist.objects.all()
    serializer_class = SpecialistSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        clinic_id = self.request.query_params.get('clinic')
        if clinic_id:
            return self.queryset.filter(clinic_id=clinic_id)
        return self.queryset.none()

class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    """
    SuperAdmin management of available plans.
    """
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsSuperAdmin]

class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    SuperAdmin management of clinic subscriptions.
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsSuperAdmin]

class RoomViewSet(ClinicIsolationMixin, viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

class BedViewSet(ClinicIsolationMixin, viewsets.ModelViewSet):
    queryset = Bed.objects.all()
    serializer_class = BedSerializer
    permission_classes = [permissions.IsAuthenticated]

class SpecialistScheduleViewSet(ClinicIsolationMixin, viewsets.ModelViewSet):
    queryset = SpecialistSchedule.objects.all()
    serializer_class = SpecialistScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

class BrandingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint para obtener la configuración visual de la clínica actual.
    """
    serializer_class = DynamicBrandingSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        clinic = getattr(self.request, 'clinic', None)
        if clinic:
            return DynamicBrandingEngine.objects.filter(clinic=clinic)
        return DynamicBrandingEngine.objects.none()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
