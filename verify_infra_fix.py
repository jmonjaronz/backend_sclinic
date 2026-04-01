#verify_infra_fix.py
import os
import django

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

from core.models.tenant import Clinic, set_current_clinic, get_current_clinic
from clinics.models import Headquarters
from django.db import connection

def verify_isolation():
    setup_django()
    from core.models.tenant import Clinic, set_current_clinic, get_current_clinic
    from clinics.models import Headquarters
    from clinics.views import PublicHeadquartersViewSet
    from django.test import RequestFactory

    # 1. Crear Clínicas de Prueba
    c1, _ = Clinic.objects.get_or_create(name="Clinica A", subdomain="clinica-a")
    c2, _ = Clinic.objects.get_or_create(name="Clinica B", subdomain="clinica-b")

    # 2. Crear Datos Aislados en el manager global directo (sin contexto)
    Headquarters.global_objects.get_or_create(name="HQ A", clinic=c1)
    Headquarters.global_objects.get_or_create(name="HQ B", clinic=c2)

    print("\n--- Verificando Aislamiento a Nivel de Manager (Fail-Closed) ---")
    
    # Caso 0: Sin contexto (Debe ser Vacío)
    set_current_clinic(None)
    qs_none = Headquarters.objects.all()
    print(f"Sin contexto: {qs_none.count()} sedes (Esperado: 0)")
    assert qs_none.count() == 0, "ERROR: Se filtraron datos sin contexto de clínica!"

    # Caso 1: Contexto Clinica A
    set_current_clinic(c1)
    qs_a = Headquarters.objects.all()
    print(f"Contexto Clinica A: {qs_a.count()} sedes (Nombres: {[h.name for h in qs_a]})")
    assert all(h.clinic == c1 for h in qs_a), "ERROR: Cruce de datos en Clinica A!"

    # Caso 2: Contexto Clinica B
    set_current_clinic(c2)
    assert Headquarters.objects.count() == 1, "ERROR: C1 debe ver solo su propia sede"

    print("\n✅ AISLAMIENTO DE DATOS CORRECTO")

    # 6. Verificar GlobalManager (metodo de escape)
    print("\nVerificando escape GlobalManager...")
    total_hqs = Headquarters.global_objects.count()
    print(f"Total sedes (GlobalObjects): {total_hqs}")
    assert total_hqs >= 2, "ERROR: global_objects debería ver todo"

    print("✅ GLOBAL MANAGER CORRECTO")

if __name__ == "__main__":
    try:
        verify_isolation()
    except Exception as e:
        print(f"\n❌ ERROR EN VERIFICACIÓN: {e}")
        import traceback
        traceback.print_exc()
