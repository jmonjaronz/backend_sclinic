from .auth_views import RegisterView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-registration'),
    path('login/', LoginView.as_view(), name='user-login'),
]
