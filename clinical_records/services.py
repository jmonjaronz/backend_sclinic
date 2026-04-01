#clinical_records/services.py
class AutocompleteService:
    """
    Servicio para autocompletar texto en historias clínicas mediante atajos (ej. /normal)
    y para buscar diagnósticos CIE-10.
    En una implementación real completa, esto se conectaría a un modelo de base de datos
    o a una API externa de CIE-10/SMOMED CT.
    """
    
    @staticmethod
    def expand_shortcut(shortcut_code: str, clinic_id) -> str:
        """
        Busca un atajo configurado por la clínica y devuelve el texto expandido.
        """
        # Aquí buscaríamos en la DB: Shortcut.objects.filter(clinic_id=clinic_id, code=shortcut_code)
        # Mock para demostración:
        mock_shortcuts = {
            "/normal": "Paciente se encuentra consciente, orientado en tiempo, espacio y persona. Sin alteraciones agudas evidentes.",
            "/cfv": "Funciones vitales estables, afebril, hemodinámicamente estable."
        }
        return mock_shortcuts.get(shortcut_code, "")
        
    @staticmethod
    def search_diagnosis(query: str):
        """
        Busca un diagnóstico por nombre o código CIE-10.
        """
        # Mock de búsqueda CIE-10
        mock_db = [
            {"code": "J00", "name": "Rinofaringitis aguda [resfriado común]"},
            {"code": "F32.0", "name": "Episodio depresivo leve"},
            {"code": "E11.9", "name": "Diabetes mellitus tipo 2 sin complicaciones"}
        ]
        
        results = [
            d for d in mock_db 
            if query.lower() in d['code'].lower() or query.lower() in d['name'].lower()
        ]
        return results

class PrescriptionService:
    """
    Handles clinical logic for prescriptions, including allergy validation.
    Req: 11_HCE.md sec. 4 - Recetario Digital
    """
    
    @staticmethod
    def check_allergies(patient, medication_list):
        """
        Cross-checks a list of medications against patient's known allergies.
        Returns a list of detected conflicts.
        """
        # In a real system, we would have a mapping of medications to components
        # or use an external pharmacological API.
        # Here we do a simple string match against noted allergies.
        
        # Get patient allergies from VitalSigns (Triage) or ClinicalRecord antecedents
        detected_conflicts = []
        
        # 1. Check VitalSigns (most recent triage)
        from .models import VitalSigns
        latest_vitals = VitalSigns.objects.filter(patient=patient).order_by('-created_at').first()
        allergies_text = ""
        if latest_vitals:
            allergies_text += latest_vitals.allergy_notes.lower()
            
        # 2. Check ClinicalRecord antecedents
        if hasattr(patient, 'clinical_record'):
            ante = patient.clinical_record.general_antecedents.get('allergies', "")
            if isinstance(ante, str):
                allergies_text += " " + ante.lower()

        if not allergies_text.strip():
            return []

        for med in medication_list:
            # Simple keyword search
            # med can be a string or a dict with 'name'
            med_name = med.get('name', '').lower() if isinstance(med, dict) else med.lower()
            
            if med_name and med_name in allergies_text:
                detected_conflicts.append({
                    "medication": med_name,
                    "conflict": f"Coincidencia directa con alergia reportada: '{med_name}'"
                })
        
        return detected_conflicts
