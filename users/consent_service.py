"""
ConsentService – Validación de consentimientos del paciente.
Req: 2_Usuarios_Permisos.md sec. 2.6 y 4.6 – ConsentManagement Activo.
"""
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied


class ConsentService:
    """
    Gestiona la validación de consentimientos del paciente antes de acceder
    a información clínica sensible o crear registros médicos.
    """

    @staticmethod
    def assert_patient_has_valid_consent(patient, consent_type: str = None):
        """
        Verifica que el paciente tenga un consentimiento clínico vigente.
        Lanza PermissionDenied si no hay consentimiento válido.

        Req: 2_Usuarios_Permisos.md sec. 4.6:
            if not patient.has_valid_consent("medical_data"):
                raise PermissionDenied("Consentimiento requerido")

        Args:
            patient: instancia de patients.Patient
            consent_type: DocumentType (e.g. 'CLINICAL', 'PRIVACY'). Si None, valida cualquiera vigente.
        """
        from users.models import PatientConsent, ConsentDocument

        qs = PatientConsent.objects.filter(
            patient=patient,
            document__is_current=True,
        )

        if consent_type:
            qs = qs.filter(document__document_type=consent_type)

        # Verificar que el consentimiento clínico base existe
        if not qs.exists():
            consent_label = consent_type or "clínico"
            raise PermissionDenied(
                f"El paciente no tiene un consentimiento {consent_label} vigente firmado. "
                f"Solicite al paciente que firme el consentimiento antes de proceder."
            )

    @staticmethod
    def patient_has_valid_consent(patient, consent_type: str = None) -> bool:
        """
        Versión booleana de assert_patient_has_valid_consent.
        Retorna True si el paciente tiene consentimiento válido, False si no.
        """
        try:
            ConsentService.assert_patient_has_valid_consent(patient, consent_type)
            return True
        except PermissionDenied:
            return False

    @staticmethod
    def get_consent_status(patient) -> dict:
        """
        Retorna un resumen del estado de consentimientos del paciente
        para todos los tipos de documentos.
        """
        from users.models import ConsentDocument

        result = {}
        for doc_type in ConsentDocument.DocumentType.values:
            result[doc_type] = ConsentService.patient_has_valid_consent(patient, doc_type)
        return result
