from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, AvailabilityBlockViewSet, TreatmentPlanViewSet

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet)
router.register(r'blocks', AvailabilityBlockViewSet)
router.register(r'treatment-plans', TreatmentPlanViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
