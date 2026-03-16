import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_sclinic.settings')
django.setup()

apps = [
    'core',
    'users',
    'patients',
    'clinics',
    'companies',
    'discounts',
    'appointments',
    'clinical_records',
]

for app in apps:
    print(f"--- Checking {app} ---")
    print(f"Importing {app}.models...")
    try:
        __import__(f"{app}.models")
        print(f"Successfully imported {app}.models")
    except Exception as e:
        print(f"FAILED to import {app}.models: {e}")
        import traceback
        traceback.print_exc()

    print(f"Importing {app}.serializers...")
    try:
        __import__(f"{app}.serializers")
        print(f"Successfully imported {app}.serializers")
    except Exception as e:
        print(f"FAILED to import {app}.serializers: {e}")
        # traceback.print_exc()

    print(f"Importing {app}.views...")
    try:
        __import__(f"{app}.views")
        print(f"Successfully imported {app}.views")
    except Exception as e:
        print(f"FAILED to import {app}.views: {e}")
        # traceback.print_exc()
