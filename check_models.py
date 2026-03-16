import os
import django
import sys
from django.core.management import call_command

print("Setting up django...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    django.setup()
    print("Django setup complete. Running checks...")
    call_command('check')
    print("SUCCESS: No issues found.")
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
