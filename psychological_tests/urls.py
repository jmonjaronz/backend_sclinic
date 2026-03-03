from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PsychologicalTestViewSet, TestApplicationViewSet

router = DefaultRouter()
router.register(r'tests', PsychologicalTestViewSet)
router.register(r'applications', TestApplicationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
