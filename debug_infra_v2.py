import os
import django
import sys

print("DEBUG: Iniciando script")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
try:
    django.setup()
    print("DEBUG: Django setup OK")
    from clinics.models import UsageMetric
    print("DEBUG: UsageMetric import OK")
    print("DEBUG: Recuento:", UsageMetric.objects.count())
except Exception as e:
    print(f"DEBUG: Error: {e}")
    import traceback
    traceback.print_exc()
