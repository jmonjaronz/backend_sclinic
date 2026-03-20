from celery import shared_task
from core.utils.celery_utils import tenant_task
import logging

logger = logging.getLogger(__name__)

@shared_task
@tenant_task
def send_clinic_notification(clinic_id, title, message):
    """
    Tarea asíncrona para enviar una notificación. El decorador @tenant_task
    asegura que get_current_clinic() devuelva la clínica correcta.
    """
    from core.models.tenant import get_current_clinic
    clinic = get_current_clinic()
    
    # Simulación de envío
    logger.info(f"Enviando notificación para {clinic.name}: '{title}' -> {message}")
    
    # Aquí iría la lógica de envío (Email, Push, etc.)
    return f"Notificación enviada para {clinic.name}"
