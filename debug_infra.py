import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
print("Django setup success")
from clinics.models import UsageMetric
print("UsageMetric import success")
