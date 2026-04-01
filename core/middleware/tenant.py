#core/middleware/tenant.py
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.conf import settings
from core.models import Clinic
from core.models.tenant import set_current_clinic, set_current_user

class MultiDomainMiddleware(MiddlewareMixin):
    """
    Middleware que identifica la clínica basándose en el subdominio o un header.
    Inyecta el objeto Clinic en el request y en el context-local storage para el Manager.
    Incluye validación de host y cache para optimizar performance.
    """
    
    def process_request(self, request):
        # 0. Definir rutas públicas que no requieren contexto de clínica
        # (Esto se puede mover a settings si crece)
        public_paths = ['/admin/', '/api/auth/', '/health/']
        if any(request.path.startswith(path) for path in public_paths):
            return None

        # 1. Intentar obtener el subdominio desde el header (útil si el frontend está en otro dominio)
        subdomain = request.headers.get('X-Clinic-Subdomain')
        
        # 2. Si no hay header, intentar obtenerlo del Host (ej: empresa-a.sclinic.com)
        if not subdomain:
            host = request.get_host().split(':')[0] # Ignorar puerto
            
            # PROTECCIÓN: Host Header Attack
            allowed_domains = getattr(settings, 'ALLOWED_TENANT_DOMAINS', [])
            if allowed_domains and not any(host.endswith(domain) for domain in allowed_domains):
                return HttpResponseForbidden("Host Header Attack Detectado o Dominio No Autorizado.")
                
            host_parts = host.split('.')
            if len(host_parts) > 2:
                # Caso: subdominio.dominio.com -> tomamos 'subdominio'
                subdomain = host_parts[0]
            else:
                subdomain = None

        clinic = None
        if subdomain:
            # 3. Buscar en cache para evitar hits constantes a la BD
            cache_key = f"clinic_subdomain_{subdomain}"
            clinic_id = cache.get(cache_key)
            
            if clinic_id:
                try:
                    clinic = Clinic.objects.get(id=clinic_id, status=Clinic.Status.ACTIVE)
                except Clinic.DoesNotExist:
                    cache.delete(cache_key)
            
            if not clinic:
                try:
                    clinic = Clinic.objects.get(subdomain=subdomain, status=Clinic.Status.ACTIVE)
                    # Cachear por 1 hora (3600s)
                    cache.set(cache_key, clinic.id, 3600)
                except Clinic.DoesNotExist:
                    clinic = None

        # 4. Asignar clínica al request y al contexto global
        request.clinic = clinic
        set_current_clinic(clinic)

        # 5. Capturar usuario (si está autenticado)
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_current_user(request.user)
        else:
            set_current_user(None)

        # 6. Fallback de seguridad: Si no hay clínica y no es ruta pública -> Bloquear
        if not request.clinic:
            return HttpResponseForbidden("Acceso denegado: No se identificó una clínica válida.")

        return None

    def process_response(self, request, response):
        """Limpia el contexto al finalizar la petición."""
        set_current_clinic(None)
        set_current_user(None)
        return response
