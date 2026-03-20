from rest_framework.exceptions import PermissionDenied
from core.models.tenant import get_current_clinic

class ClinicIsolationMixin:
    """
    Mixin de DRF para ViewSets que garantiza que las consultas estén restringidas
    a la clínica activa en el contexto global (ContextVar).
    """

    def get_queryset(self):
        """
        Sobrescribe get_queryset para asegurar la restricción por clínica en la API.
        Falla segura: Si no hay clínica en el contexto, retorna un queryset vacío.
        """
        assert self.queryset is not None, (
            "'%s' no definió el atributo `queryset`."
            % self.__class__.__name__
        )
        
        clinic = get_current_clinic()
        qs = super().get_queryset()

        if clinic:
            # Si el modelo hereda de ClinicAwareModel, el filtrado ya ocurre en el manager,
            # pero lo hacemos explícito para ser consistentes con modelos que no hereden de él.
            if hasattr(qs.model, 'clinic'):
                return qs.filter(clinic=clinic)
            return qs 
        
        # Falla Segura: Si no hay clínica en el contexto, no devuelve nada
        return qs.none()

    def perform_create(self, serializer):
        """
        Asigna automáticamente la clínica al crear un registro desde la API.
        """
        clinic = get_current_clinic()
        if clinic:
            serializer.save(clinic=clinic)
        else:
            raise PermissionDenied("Debe realizar la petición desde un contexto de clínica válido.")
