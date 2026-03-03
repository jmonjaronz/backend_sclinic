from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class DocumentAuthBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using 
    their document type, document number, and password.
    """
    def authenticate(self, request, document_type=None, document_number=None, password=None, **kwargs):
        if not document_type or not document_number or not password:
            # Fallback to standard username auth if those aren't provided
            username = kwargs.get('username')
            if username:
                 try:
                    user = User.objects.get(username=username)
                    if user.check_password(password):
                        return user
                 except User.DoesNotExist:
                    return None
            return None

        try:
            # Multi-tenant consideration: If clinic is in the request or kwargs, we should filter by it.
            # However, document_type + document_number + clinic is unique.
            # For simplicity in the first step, we assume document_type + document_number is unique enough if we have the clinic.
            # If clinic is not provided, we might have issues if multiple clinics have the same DNI.
            
            clinic_id = kwargs.get('clinic_id')
            filters = {
                'document_type': document_type,
                'document_number': document_number
            }
            if clinic_id:
                filters['clinic_id'] = clinic_id
                
            user = User.objects.get(**filters)
            if user.check_password(password):
                return user
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
