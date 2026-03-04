from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublicClinicViewSet, PublicHeadquartersViewSet, PublicServiceViewSet, PublicSpecialistViewSet, SubscriptionPlanViewSet, SubscriptionViewSet
from .admin_views import SuperAdminDashboardView

router = DefaultRouter()
router.register(r'public-clinics', PublicClinicViewSet)
router.register(r'public-headquarters', PublicHeadquartersViewSet)
router.register(r'public-services', PublicServiceViewSet)
router.register(r'public-specialists', PublicSpecialistViewSet)
router.register(r'admin/plans', SubscriptionPlanViewSet, basename='admin-plans')
router.register(r'admin/subscriptions', SubscriptionViewSet, basename='admin-subscriptions')

urlpatterns = [
    path('admin/dashboard/', SuperAdminDashboardView.as_view(), name='superadmin-dashboard'),
    path('', include(router.urls)),
]
