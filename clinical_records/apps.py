from django.apps import AppConfig

class ClinicalRecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clinical_records'

    def ready(self):
        import clinical_records.signals
