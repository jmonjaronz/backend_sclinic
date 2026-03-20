from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        # El modelo Clinic ya existe en la DB pero Django lo busca en 'core'
        # Añadimos la definición de estado para que las dependencias funcionen.
        migrations.CreateModel(
            name='Clinic',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('subdomain', models.SlugField(unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('min_booking_days_notice', models.IntegerField(default=1)),
                ('payment_required_before', models.BooleanField(default=True)),
                ('payment_grace_period_days', models.IntegerField(default=1)),
                ('max_reschedules_allowed', models.IntegerField(default=2)),
                ('reschedule_notice_hours', models.IntegerField(default=24)),
                ('cancel_notice_hours', models.IntegerField(default=24)),
                ('requires_triage_before_appointment', models.BooleanField(default=False)),
            ],
            options={
                'swappable': 'core.Clinic',
            },
        ),
    ]
