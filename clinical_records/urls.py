from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClinicalRecordViewSet, SessionNoteViewSet, EmergencyAdmissionViewSet, HospitalizationViewSet, TreatmentViewSet

router = DefaultRouter()
router.register(r'records', ClinicalRecordViewSet, basename='clinical-records')
router.register(r'session-notes', SessionNoteViewSet, basename='session-notes')
router.register(r'emergencies', EmergencyAdmissionViewSet, basename='emergencies')
router.register(r'hospitalizations', HospitalizationViewSet, basename='hospitalizations')
router.register(r'treatments', TreatmentViewSet, basename='treatments')

urlpatterns = [
    path('', include(router.urls)),
]
