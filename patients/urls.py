from django.urls import path
from .views import PatientRegistrationView

urlpatterns = [
    path('register/', PatientRegistrationView.as_view(), name='patient-registration'),
]
