#psychological_tests/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TestBatteryViewSet, PsychologicalTestViewSet,
    TestApplicationViewSet, DimensionViewSet, BaremoViewSet
)

router = DefaultRouter()
router.register(r'batteries', TestBatteryViewSet, basename='test-battery')
router.register(r'catalogue', PsychologicalTestViewSet, basename='psychological-test')
router.register(r'applications', TestApplicationViewSet, basename='test-application')
router.register(r'dimensions', DimensionViewSet, basename='test-dimension')
router.register(r'baremos', BaremoViewSet, basename='test-baremo')

urlpatterns = [
    path('', include(router.urls)),
]
