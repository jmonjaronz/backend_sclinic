#medical_results/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicalResultViewSet

router = DefaultRouter()
router.register(r'results', MedicalResultViewSet, basename='medical-result')

urlpatterns = [
    path('', include(router.urls)),
]
