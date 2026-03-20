from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalAuditLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('action', models.CharField(choices=[('CREATE', 'Creación'), ('UPDATE', 'Actualización'), ('DELETE', 'Eliminación'), ('ACCESS', 'Acceso a datos sensibles')], max_length=20)),
                ('model_name', models.CharField(db_index=True, max_length=100)),
                ('object_id', models.CharField(db_index=True, max_length=255)),
                ('changes_before', models.JSONField(blank=True, null=True)),
                ('changes_after', models.JSONField(blank=True, null=True)),
                ('reason', models.TextField(blank=True)),
                ('clinic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='global_audit_logs', to='core.clinic')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='global_audit_logs', to='users.user')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
