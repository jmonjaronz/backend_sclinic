from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import B2BCompanyViewSet, CompanyAffiliationViewSet, BenefitViewSet

router = DefaultRouter()
router.register(r'companies', B2BCompanyViewSet, basename='b2b-companies')
router.register(r'affiliations', CompanyAffiliationViewSet, basename='company-affiliations')
router.register(r'benefits', BenefitViewSet, basename='benefits')

urlpatterns = [
    path('', include(router.urls)),
]
