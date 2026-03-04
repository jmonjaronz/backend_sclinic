from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, TreatmentPlanViewSet, AvailabilityBlockViewSet

router = DefaultRouter()
router.register(r'', AppointmentViewSet, basename='appointments')
router.register(r'plans', TreatmentPlanViewSet, basename='treatment-plans')
router.register(r'blocks', AvailabilityBlockViewSet, basename='availability-blocks')

urlpatterns = [
    path('', include(router.urls)),
]
