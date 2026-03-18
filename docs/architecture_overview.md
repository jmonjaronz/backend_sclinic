# Arquitectura del Sistema - SCLINIC

SCLINIC es una plataforma SaaS multi-tenant diseñada para la gestión de clínicas de salud ocupacional, psicología y medicina general.

## 1. Estructura de Aplicaciones (Apps)
- **`core/`**: Configuración central de Django, permisos SaaS globales (`IsSuperAdmin`) y utilidades comunes.
- **`users/`**: Gestión de perfiles de usuario y roles. Soporte para múltiples tipos de actores (Admin, Especialista, Paciente, Empresa). Incluye soporte para **Firmas Digitales**.
- **`clinics/`**: Núcleo del multi-tenancy. Gestión de clínicas, sedes, especialidades, servicios y el sistema de **Suscripciones y Planes**.
- **`patients/`**: Base de datos de pacientes, perfiles clínicos y vínculos familiares.
- **`appointments/`**: Motor de agendamiento, gestión de disponibilidad compleja, **Soft Locks** (bloqueos temporales) y auditoría histórica.
- **`companies/`**: Portal B2B. Convenios, empresas, nómina de empleados y protocolos médicos.
- **`insurances/`**: Gestión de aseguradoras, planes de salud y cálculo automático de copagos/coaseguros.
- **`clinical_records/`**: Historia clínica avanzada con esquemas dinámicos, buscador CIE-10 y alertas de alergias.
- **`occupational_health/`**: Flujo de evaluaciones ocupacionales, hojas de ruta y dictámenes de aptitud.
- **`psychological_tests/`**: Sistema de evaluaciones psicológicas con calificación automática.
- **`medical_results/`**: Resultados de laboratorio e imágenes vinculados a citas y notas médicas.
- **`discounts/`**: Motor de beneficios unificado para convenios y promociones.

## 2. Flujo de Datos Multi-tenant
- **Middleware de Clínica**: Todo request es interceptado para identificar la clínica activa via subdominio o header.
- **Aislamiento a nivel de QuerySet**: Los `ViewSets` filtran automáticamente por el ID de la clínica actual, previniendo fugas de datos.

## 3. Integración B2B y Salud Ocupacional
- El sistema utiliza llaves foráneas en `Appointment` hacia `Company` y `Agreement` para rastrear qué compañía financia cada servicio, permitiendo el filtrado de privacidad en los módulos de resultados.
