# Documentación del Proyecto SCLINIC

Bienvenido a la base de conocimiento centralizada de SCLINIC. Estos documentos se mantienen actualizados con el desarrollo del sistema para servir como fuente única de verdad sobre las reglas y el funcionamiento de la plataforma.

## 📂 Contenido
- [**Reglas de Negocio**](business_rules.md): Lógica central, roles, portal B2B, privacidad y pagos.
- [**Arquitectura del Sistema**](architecture_overview.md): Estructura técnica de apps Django, multi-tenancy e integración de datos.
- [**Estructura de Carpetas**](folder_structure.md): Resumen de la organización del código por dominios.
- [**Guía de Funcionalidades**](features_guide.md): Catálogo de capacidades actuales (SaaS, Citas, Tests, Resultados).
- [**Requerimientos**](requirements/README.md): Requerimientos del sistema.

## 💡 Propósito
Esta documentación está diseñada para:
1.  Facilitar el onboarding de nuevos desarrolladores.
2.  Servir de referencia rápida para reglas de privacidad y lógica corporativa.
3.  Evitar la repetición de explicaciones sobre el funcionamiento técnico de los módulos.

## 📌 Principio Clave del Proyecto
SCLINIC está diseñado como una plataforma SaaS multi-tenant para gestión clínica, donde cada clínica funciona como un entorno aislado dentro de la misma infraestructura.
- Esto implica que el sistema prioriza:
    - Aislamiento total de datos entre clínicas
    - Seguridad y trazabilidad de la información médica
    - Arquitectura escalable
    - Configuración modular del sistema