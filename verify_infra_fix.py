import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models.tenant import Clinic, set_current_clinic, get_current_clinic
from clinics.models import Headquarters
from django.db import connection

def verify_isolation():
    print("--- Verificando Aislamiento Multi-Tenant ---")
    
    # 1. Crear clínicas de prueba
    c1, _ = Clinic.objects.get_or_create(subdomain="clinic1", defaults={"name": "Clínica 1"})
    c2, _ = Clinic.objects.get_or_create(subdomain="clinic2", defaults={"name": "Clínica 2"})
    
    # 2. Verificar que sin clínica el Manager devuelve NADA
    set_current_clinic(None)
    print(f"Clínica actual: {get_current_clinic()}")
    hq_count = Headquarters.objects.count()
    print(f"Sedes visibles sin clínica: {hq_count}")
    assert hq_count == 0, "ERROR: El manager debe devolver 0 si no hay clínica set"

    # 3. Crear datos para C1
    set_current_clinic(c1)
    h1, _ = Headquarters.objects.get_or_create(clinic=c1, name="Sede C1", defaults={"city": "Lima", "address": "Av A"})
    print(f"Sedes visibles para C1: {Headquarters.objects.count()}")
    
    # 4. Cambiar a C2 y verificar aislamiento
    set_current_clinic(c2)
    print(f"Cambiando a Clínica 2...")
    h2_count = Headquarters.objects.count()
    print(f"Sedes visibles para C2: {h2_count}")
    assert h2_count == 0, "ERROR: C2 no debería ver las sedes de C1"
    
    # Crear dato para C2
    h2, _ = Headquarters.objects.get_or_create(clinic=c2, name="Sede C2", defaults={"city": "Cusco", "address": "Av B"})
    print(f"Sedes visibles para C2 tras crear una: {Headquarters.objects.count()}")

    # 5. Volver a C1
    set_current_clinic(c1)
    print(f"Volviendo a Clínica 1...")
    print(f"Sedes visibles para C1: {Headquarters.objects.count()}")
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
