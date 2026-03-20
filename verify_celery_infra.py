import os
import django

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

def verify_celery_task_isolation():
    setup_django()
    from core.models.tenant import Clinic, get_current_clinic, set_current_clinic
    from notifications.tasks import send_clinic_notification
    from clinics.models import Headquarters
    import logging

    # Desactivar logs ruidosos
    logging.getLogger('core.utils.celery_utils').setLevel(logging.INFO)

    # 1. Preparar clínicas
    c1, _ = Clinic.objects.get_or_create(name="Clinica Alpha", subdomain="alpha")
    c2, _ = Clinic.objects.get_or_create(name="Clinica Beta", subdomain="beta")

    print("\n--- Verificando Aislamiento en Tareas de Celery ---")

    # Caso A: Ejecutando tarea para Clinica Alpha
    print(f"Llamando a tarea para {c1.name} (ID: {c1.id})...")
    # Nota: Llamamos a la función directamente para probar la lógica del decorador @tenant_task
    # sin requerir un worker de Redis activo en este entorno.
    result_a = send_clinic_notification(c1.id, "Test Alpha", "Hola Alpha")
    print(f"Resultado A: {result_a}")
    
    # Verificar que el contexto se limpió después de la tarea
    assert get_current_clinic() is None, "ERROR: El contexto de clínica no se limpió tras la tarea A!"

    # Caso B: Ejecutando tarea para Clinica Beta
    print(f"Llamando a tarea para {c2.name} (ID: {c2.id})...")
    result_b = send_clinic_notification(c2.id, "Test Beta", "Hola Beta")
    print(f"Resultado B: {result_b}")
    
    assert get_current_clinic() is None, "ERROR: El contexto de clínica no se limpió tras la tarea B!"

    # Caso C: Verificar que dentro de la tarea el Manager filtró correctamente
    # (Esto se prueba indirectamente porque send_clinic_notification imprime clinic.name)
    # Vamos a hacer una prueba más explícita con una tarea interna de prueba
    
    from celery import shared_task
    from core.utils.celery_utils import tenant_task

    @shared_task
    @tenant_task
    def check_manager_in_task(clinic_id):
        from clinics.models import Headquarters
        count = Headquarters.objects.count()
        current = get_current_clinic()
        return {"count": count, "clinic": str(current)}

    # Crear una sede en cada clínica
    Headquarters.global_objects.get_or_create(name="Sede Alpha", clinic=c1)
    Headquarters.global_objects.get_or_create(name="Sede Beta", clinic=c2)

    res_alpha = check_manager_in_task(c1.id)
    print(f"Manager en Tarea Alpha: {res_alpha}")
    assert res_alpha['count'] == 1, "ERROR: El manager devolvió más de una sede (o ninguna) en la tarea Alpha!"

    res_beta = check_manager_in_task(c2.id)
    print(f"Manager en Tarea Beta: {res_beta}")
    assert res_beta['count'] == 1, "ERROR: El manager devolvió más de una sede (o ninguna) en la tarea Beta!"

    print("\n✅ LA INFRAESTRUCTURA DE CELERY MULT-TENANT ES SEGURA (REGLA 4.2 OK).")

if __name__ == "__main__":
    verify_celery_task_isolation()
