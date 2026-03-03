from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import B2BCompanyViewSet, BenefitViewSet, CompanyAffiliationViewSet, DiscountCheckViewSet

router = DefaultRouter()
router.register(r'companies', B2BCompanyViewSet)
router.register(r'benefits', BenefitViewSet)
router.register(r'affiliations', CompanyAffiliationViewSet)
router.register(r'check', DiscountCheckViewSet, basename='discount-check')

urlpatterns = [
    path('', include(router.urls)),
]
