from rest_framework import viewsets, permissions
from .models import Clinic, Headquarters, Specialty, Service, Specialist, SubscriptionPlan, Subscription, Room, Bed
from .serializers import (
    ClinicSerializer, HeadquartersSerializer, SpecialtySerializer, 
    ServiceSerializer, SpecialistSerializer, SubscriptionPlanSerializer, 
    SubscriptionSerializer, RoomSerializer, BedSerializer
)
from core.permissions import IsSuperAdmin

class PublicClinicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public access to clinic data.
    """
    queryset = Clinic.objects.filter(is_active=True)
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
        return self.queryset

class PublicServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        clinic_id = self.request.query_params.get('clinic')
        if clinic_id:
            return self.queryset.filter(clinic_id=clinic_id)
        return self.queryset

class PublicSpecialistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialist.objects.all()
    serializer_class = SpecialistSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        clinic_id = self.request.query_params.get('clinic')
        if clinic_id:
            return self.queryset.filter(clinic_id=clinic_id)
        return self.queryset

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

class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Room.objects.all()
        if hasattr(user, 'clinic') and user.clinic:
            qs = qs.filter(headquarters__clinic=user.clinic)
        return qs

class BedViewSet(viewsets.ModelViewSet):
    serializer_class = BedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Bed.objects.all()
        if hasattr(user, 'clinic') and user.clinic:
            qs = qs.filter(room__headquarters__clinic=user.clinic)
        return qs

class SpecialistScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = SpecialistScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = SpecialistSchedule.objects.all()
        if hasattr(user, 'clinic') and user.clinic:
            qs = qs.filter(specialist__clinic=user.clinic)
        return qs
