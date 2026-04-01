#clinics/middleware.py
from django.utils.deprecation import MiddlewareMixin
from clinics.models import Clinic

class ClinicMiddleware(MiddlewareMixin):
    """
    Middleware que identifica la clínica basándose en el subdominio o un header.
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
                clinic = Clinic.objects.get(subdomain=subdomain, status='active')
                request.clinic = clinic
            except Clinic.DoesNotExist:
                # Si el subdominio no existe y no es una ruta de admin/core, podríamos lanzar 404
                # Pero permitiremos que siga si la ruta es pública o admin, el view decidirá si requiere clinic.
                request.clinic = None
        else:
            request.clinic = None

        return None
