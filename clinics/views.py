from rest_framework import viewsets, permissions
from .models import Clinic, Headquarters, Specialty, Service, Specialist, SubscriptionPlan, Subscription
from .serializers import ClinicSerializer, HeadquartersSerializer, SpecialtySerializer, ServiceSerializer, SpecialistSerializer, SubscriptionPlanSerializer, SubscriptionSerializer
from core.permissions import IsSuperAdmin

class PublicClinicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public access to clinic data.
    """
    queryset = Clinic.objects.filter(is_active=True)
    serializer_class = ClinicSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'subdomain'

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
