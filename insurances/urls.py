from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InsurerViewSet, InsurancePlanViewSet, InsuranceCoverageViewSet

router = DefaultRouter()
router.register(r'insurers', InsurerViewSet)
router.register(r'plans', InsurancePlanViewSet)
router.register(r'coverages', InsuranceCoverageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
