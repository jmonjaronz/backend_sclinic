from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('clinics', '0005_remove_service_max_capacity_headquarters_email_and_more'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DynamicBrandingEngine',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('logo_url', models.ImageField(blank=True, null=True, upload_to='clinic_logos/')),
                ('primary_color', models.CharField(default='#000000', max_length=7)),
                ('secondary_color', models.CharField(default='#FFFFFF', max_length=7)),
                ('nomenclature_patient', models.CharField(default='Paciente', max_length=50)),
                ('nomenclature_specialist', models.CharField(default='Especialista', max_length=50)),
                ('clinic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_objects', to='core.clinic')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UsageMetric',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('metric_code', models.CharField(help_text='Ej: appointments_monthly, specialists_active', max_length=50)),
                ('value', models.PositiveIntegerField(default=0)),
                ('period', models.CharField(help_text='Ej: 2026-03, ALL_TIME', max_length=20)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('clinic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_objects', to='core.clinic')),
            ],
            options={
                'unique_together': {('clinic', 'metric_code', 'period')},
            },
        ),
    ]
