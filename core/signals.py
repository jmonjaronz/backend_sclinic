#core/signals.py
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models.tenant import ClinicAwareModel, get_current_user, get_current_clinic
from .models.audit import GlobalAuditLog

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    """Captura el estado anterior del objeto antes de guardar."""
    if not isinstance(instance, ClinicAwareModel):
        return

    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_state = model_to_dict(old_instance)
        except sender.DoesNotExist:
            instance._old_state = None
    else:
        instance._old_state = None

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    """Registra la creación o actualización en el log global."""
    if not isinstance(instance, ClinicAwareModel):
        return

    user = get_current_user()
    clinic = instance.clinic if hasattr(instance, 'clinic') else get_current_clinic()

    if not clinic:
        return # No auditamos si no hay contexto de clínica (ej: scripts de sistema sin clínica)

    action = GlobalAuditLog.Action.CREATE if created else GlobalAuditLog.Action.UPDATE
    
    # Serializar cambios
    new_state = model_to_dict(instance)
    old_state = getattr(instance, '_old_state', None)

    GlobalAuditLog.objects.create(
        user=user,
        clinic=clinic,
        action=action,
        model_name=sender.__name__,
        object_id=str(instance.pk),
        changes_before=old_state,
        changes_after=new_state
    )

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    """Registra la eliminación del objeto."""
    if not isinstance(instance, ClinicAwareModel):
        return

    user = get_current_user()
    clinic = instance.clinic if hasattr(instance, 'clinic') else get_current_clinic()

    if not clinic:
        return

    GlobalAuditLog.objects.create(
        user=user,
        clinic=clinic,
        action=GlobalAuditLog.Action.DELETE,
        model_name=sender.__name__,
        object_id=str(instance.pk),
        changes_before=model_to_dict(instance),
        changes_after=None
    )
