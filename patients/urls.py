from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientRegistrationView, PatientViewSet

router = DefaultRouter()
router.register(r'', PatientViewSet, basename='patients')

urlpatterns = [
    path('register/', PatientRegistrationView.as_view(), name='patient-register'),
    path('', include(router.urls)),
]
