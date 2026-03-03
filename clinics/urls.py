from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublicClinicViewSet, PublicHeadquartersViewSet, PublicServiceViewSet, PublicSpecialistViewSet

router = DefaultRouter()
router.register(r'public-clinics', PublicClinicViewSet)
router.register(r'public-headquarters', PublicHeadquartersViewSet)
router.register(r'public-services', PublicServiceViewSet)
router.register(r'public-specialists', PublicSpecialistViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
