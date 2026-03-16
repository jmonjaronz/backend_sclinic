from rest_framework.exceptions import PermissionDenied

class ClinicIsolationMixin:
    """
    Mixin de DRF para ViewSets que garantiza que las consultas estén restringidas
    a la clínica activa en el request (identificada por MultiDomainMiddleware).
    """

    def get_queryset(self):
        """
        Sobrescribe get_queryset para asegurar la restricción por clínica en la API.
        Falla segura: Si no hay clínica en el request, retorna un queryset vacío.
        """
        assert self.queryset is not None, (
            "'%s' no definió el atributo `queryset`."
            % self.__class__.__name__
        )
        qs = super().get_queryset()

        if hasattr(self.request, 'clinic') and self.request.clinic:
            # Si el modelo hereda de ClinicAwareModel, filter(clinic=...) será redundante 
            # gracias a ClinicGlobalManager, pero lo hacemos por seguridad si el modelo 
            # no hereda de ClinicAwareModel sino que tiene la FK manual.
            if hasattr(qs.model, 'clinic'):
                return qs.filter(clinic=self.request.clinic)
            return qs 
        
        # Falla Segura: Si no hay clínica en el contexto, no devuelve nada
        return qs.none()

    def perform_create(self, serializer):
        """
        Asigna automáticamente la clínica al crear un registro desde la API.
        """
        if hasattr(self.request, 'clinic') and self.request.clinic:
            serializer.save(clinic=self.request.clinic)
        else:
            raise PermissionDenied("Debe realizar la petición desde un dominio de clínica válido.")
