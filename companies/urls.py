#companies/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, AgreementViewSet, EmployeeViewSet

router = DefaultRouter()
router.register(r'profiles', CompanyViewSet, basename='company-profile')
router.register(r'agreements', AgreementViewSet, basename='agreement')
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('', include(router.urls)),
]
