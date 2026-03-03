from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClinicalRecordViewSet, SessionNoteViewSet

router = DefaultRouter()
router.register(r'records', ClinicalRecordViewSet)
router.register(r'session-notes', SessionNoteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
