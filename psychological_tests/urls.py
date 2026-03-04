from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestBatteryViewSet, PsychologicalTestViewSet, TestApplicationViewSet

router = DefaultRouter()
router.register(r'batteries', TestBatteryViewSet, basename='test-battery')
router.register(r'catalogue', PsychologicalTestViewSet, basename='psychological-test')
router.register(r'applications', TestApplicationViewSet, basename='test-application')

urlpatterns = [
    path('', include(router.urls)),
]
