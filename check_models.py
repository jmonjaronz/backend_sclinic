import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.apps import apps

with open("check_out.txt", "w", encoding='utf-8') as f:
    try:
        users_app = apps.get_app_config('users')
        f.write("Models in users app: " + str([m.__name__ for m in users_app.get_models()]) + "\n")
        
        # Test if makemigrations recognizes it programmatically
        from django.core.management import call_command
        import sys
        f.write("Running call_command makemigrations...\n")
        with open("makemig_out.txt", "w", encoding='utf-8') as sys.stdout:
            call_command("makemigrations", "users", dry_run=True, verbosity=3)
            
    except Exception as e:
        f.write(f"ERROR: {str(e)}\n")
