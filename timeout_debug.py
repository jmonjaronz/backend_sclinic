import os
import django
import threading
import importlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

def timeout_import(module_name):
    print(f"Trying to import {module_name}...", end=" ", flush=True)
    
    result = {"success": False, "error": None}
    
    def do_import():
        try:
            importlib.import_module(module_name)
            result["success"] = True
        except Exception as e:
            result["error"] = e

    thread = threading.Thread(target=do_import)
    thread.daemon = True
    thread.start()
    thread.join(timeout=5)
    
    if thread.is_alive():
        print("TIMED OUT!")
        return False
    elif result["success"]:
        print("OK")
        return True
    else:
        print(f"FAILED: {result['error']}")
        return False

# List of all modules to check
modules = [
    'core.models',
    'users.models',
    'patients.models',
    'clinics.models',
    'companies.models',
    'discounts.models',
    'appointments.models',
    'clinical_records.models',
    'discounts.logic',
    'discounts.views',
    'companies.views',
    'clinics.views',
]

for m in modules:
    if not timeout_import(m):
        # If it timed out, we might want to know where it's stuck
        pass

print("\n--- Starting django.setup() ---")
def do_setup():
    try:
        django.setup()
        print("django.setup() OK")
    except Exception as e:
        print(f"django.setup() FAILED: {e}")

setup_thread = threading.Thread(target=do_setup)
setup_thread.daemon = True
setup_thread.start()
setup_thread.join(timeout=10)
if setup_thread.is_alive():
    print("django.setup() TIMED OUT!")
