from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PsychologicalTestViewSet, TestApplicationViewSet

router = DefaultRouter()
router.register(r'tests', PsychologicalTestViewSet, basename='tests')
router.register(r'applications', TestApplicationViewSet, basename='test-applications')

urlpatterns = [
    path('', include(router.urls)),
]
