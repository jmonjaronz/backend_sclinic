from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import Company

User = get_user_model()

class CompanyAuthBackend(ModelBackend):
    """
    Custom authentication backend for B2B portal.
    Requires RUC, Razon Social, and Username.
    """
    def authenticate(self, request, ruc=None, razon_social=None, username=None, password=None, **kwargs):
        if not ruc or not razon_social or not username or not password:
            return None

        try:
            # First, find the company
            company = Company.objects.get(ruc=ruc, razon_social=razon_social, is_active=True)
            
            # Check if the user is the manager of this company
            user = User.objects.get(username=username, managed_company=company)
            
            if user.check_password(password):
                return user
        except (Company.DoesNotExist, User.DoesNotExist):
            return None
            
        return None
