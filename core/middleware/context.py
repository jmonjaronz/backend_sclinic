#core/middleware/context.py
from django.utils.deprecation import MiddlewareMixin
from users.models import User

class ContextMiddleware(MiddlewareMixin):
    """
    Middleware que extrae el header X-App-Context y lo inyecta en el request.
    Valida que el contexto pertenezca a User.PortalType.
    """
    def process_request(self, request):
        app_context = request.headers.get('X-App-Context')
        
        # Extraer los valores válidos de PortalType
        valid_contexts = [choice[0] for choice in User.PortalType.choices]
        
        if app_context and app_context not in valid_contexts:
            app_context = None
            
        request.app_context = app_context
        return None
