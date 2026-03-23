from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .auth_views import RegisterView, LoginView
from .views import (
    CapabilityViewSet,
    RoleTemplateViewSet,
    DynamicRoleViewSet,
    UserRoleViewSet,
    SwitchActiveRoleView,
)

router = DefaultRouter()
router.register(r'capabilities', CapabilityViewSet, basename='capability')
router.register(r'role-templates', RoleTemplateViewSet, basename='role-template')
router.register(r'dynamic-roles', DynamicRoleViewSet, basename='dynamic-role')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-registration'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('me/switch-role/', SwitchActiveRoleView.as_view(), name='user-switch-role'),
    path('', include(router.urls)),
]
