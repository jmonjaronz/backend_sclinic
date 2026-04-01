#occupational_health/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OccupationalEvaluationViewSet, EvaluationServiceStatusViewSet, AptitudeDictumViewSet

router = DefaultRouter()
router.register(r'evaluations', OccupationalEvaluationViewSet)
router.register(r'service-status', EvaluationServiceStatusViewSet)
router.register(r'dictums', AptitudeDictumViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
