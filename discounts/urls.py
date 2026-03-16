from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BenefitViewSet

router = DefaultRouter()
router.register(r'benefits', BenefitViewSet, basename='benefits')

urlpatterns = [
    path('', include(router.urls)),
]
