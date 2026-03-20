import functools
from core.models.tenant import set_current_clinic, Clinic
import logging

logger = logging.getLogger(__name__)

def tenant_task(func):
    """
    Decorador para tareas de Celery que requieren contexto de clínica.
    Espera que 'clinic_id' sea pasado como argumento (posicional o keyword).
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        clinic_id = kwargs.get('clinic_id')
        if not clinic_id and args:
            # Intentar obtenerlo del primer argumento posicional si no está en kwargs
            clinic_id = args[0]
        
        if clinic_id:
            try:
                # Intentar obtener el objeto Clinic
                clinic = Clinic.objects.get(id=clinic_id)
                set_current_clinic(clinic)
                logger.info(f"Contexto de clínica establecido: {clinic.name} para la tarea {func.__name__}")
            except Clinic.DoesNotExist:
                logger.error(f"Error en tarea {func.__name__}: Clínica con ID {clinic_id} no existe.")
                set_current_clinic(None)
            except Exception as e:
                logger.error(f"Error al establecer contexto en tarea {func.__name__}: {str(e)}")
                set_current_clinic(None)
        else:
            logger.warning(f"Tarea {func.__name__} ejecutada sin clinic_id.")
            set_current_clinic(None)
            
        try:
            return func(*args, **kwargs)
        finally:
            # Limpiar contexto al finalizar
            set_current_clinic(None)
            
    return wrapper
