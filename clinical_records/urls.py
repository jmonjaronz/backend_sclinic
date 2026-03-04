from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClinicalRecordViewSet, SessionNoteViewSet

router = DefaultRouter()
router.register(r'records', ClinicalRecordViewSet, basename='clinical-records')
router.register(r'notes', SessionNoteViewSet, basename='session-notes')

urlpatterns = [
    path('', include(router.urls)),
]
