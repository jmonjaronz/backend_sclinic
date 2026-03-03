from django.db.models.signals import post_save
from django.dispatch import receiver
from patients.models import Patient
from .models import ClinicalRecord

@receiver(post_save, sender=Patient)
def create_clinical_record(sender, instance, created, **kwargs):
    if created:
        # We need a clinic. In multi-tenant, usually the patient is created within a clinic context.
        # Assuming Patient model has a clinic field (based on clinics/models.py or similar logic)
        # Let's check patients/models.py to be sure.
        if hasattr(instance, 'clinic') and instance.clinic:
            ClinicalRecord.objects.get_or_create(
                clinic=instance.clinic,
                patient=instance
            )
