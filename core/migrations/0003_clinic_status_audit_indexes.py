#core/migrations/0003_clinic_status_audit_indexes.py
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_audit'),
    ]

    operations = [
        # 1. Refactor Clinic status
        migrations.RemoveField(
            model_name='clinic',
            name='is_active',
        ),
        migrations.AddField(
            model_name='clinic',
            name='status',
            field=models.CharField(
                choices=[('active', 'Activa'), ('suspended', 'Suspendida'), ('disabled', 'Deshabilitada')],
                default='active',
                max_length=20,
                db_index=True
            ),
        ),
        # 2. Add Composite Indexes to GlobalAuditLog
        migrations.AddIndex(
            model_name='globalauditlog',
            index=models.Index(fields=['clinic', 'model_name'], name='core_global_clinic_96cc90_idx'),
        ),
        migrations.AddIndex(
            model_name='globalauditlog',
            index=models.Index(fields=['clinic', 'timestamp'], name='core_global_clinic_e6e30b_idx'),
        ),
    ]
