import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
print("DJANGO_SETUP_SUCCESS")
from core.models.tenant import Clinic
print(f"CLINIC_COUNT: {Clinic.objects.count()}")
