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
