from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PublicClinicViewSet, PublicHeadquartersViewSet, PublicServiceViewSet,
    PublicSpecialistViewSet, SubscriptionPlanViewSet, SubscriptionViewSet,
    AdminClinicViewSet, RoomViewSet, BedViewSet, SpecialistScheduleViewSet,
    BrandingViewSet
)
from .admin_views import SuperAdminDashboardView

router = DefaultRouter()
router.register(r'public-clinics', PublicClinicViewSet)
router.register(r'public-headquarters', PublicHeadquartersViewSet)
router.register(r'public-services', PublicServiceViewSet)
router.register(r'public-specialists', PublicSpecialistViewSet)
router.register(r'admin/plans', SubscriptionPlanViewSet, basename='admin-plans')
router.register(r'admin/subscriptions', SubscriptionViewSet, basename='admin-subscriptions')
router.register(r'admin/clinics', AdminClinicViewSet, basename='admin-clinics')
router.register(r'rooms', RoomViewSet, basename='rooms')
router.register(r'beds', BedViewSet, basename='beds')
router.register(r'schedules', SpecialistScheduleViewSet, basename='schedules')
router.register(r'branding', BrandingViewSet, basename='branding')

urlpatterns = [
    path('admin/dashboard/', SuperAdminDashboardView.as_view(), name='superadmin-dashboard'),
    path('', include(router.urls)),
]
