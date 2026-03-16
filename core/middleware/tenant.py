from django.utils.deprecation import MiddlewareMixin
from core.models import Clinic
from core.models.tenant import set_current_clinic

class MultiDomainMiddleware(MiddlewareMixin):
    """
    Middleware que identifica la clínica basándose en el subdominio o un header.
    Inyecta el objeto Clinic en el request y en el thread-local storage para el Manager.
    """
    def process_request(self, request):
        # 1. Intentar obtener el subdominio desde el header (útil si el frontend está en otro dominio)
        subdomain = request.headers.get('X-Clinic-Subdomain')
        
        # 2. Si no hay header, intentar obtenerlo del Host (ej: empresa-a.sclinic.com)
        if not subdomain:
            host = request.get_host().split(':')[0] # Ignorar puerto
            host_parts = host.split('.')
            if len(host_parts) > 2:
                # Caso: subdominio.dominio.com -> tomamos 'subdominio'
                subdomain = host_parts[0]
            else:
                # Caso local o sin subdominio definidido
                subdomain = None

        # 3. Buscar la clínica
        if subdomain:
            try:
                clinic = Clinic.objects.get(subdomain=subdomain, is_active=True)
                request.clinic = clinic
                set_current_clinic(clinic) # Inyectar para el ORM manager global
            except Clinic.DoesNotExist:
                # Si el subdominio no existe permitiremos que siga si la ruta es pública o admin.
                request.clinic = None
                set_current_clinic(None)
        else:
            request.clinic = None
            set_current_clinic(None)

        return None
