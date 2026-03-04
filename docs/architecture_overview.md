# Arquitectura del Sistema - SCLINIC

SCLINIC es una plataforma SaaS multi-tenant diseñada para la gestión de clínicas de salud ocupacional, psicología y medicina general.

## 1. Estructura de Aplicaciones (Apps)
- **`core/`**: Configuración central de Django, permisos SaaS globales (`IsSuperAdmin`) y utilidades comunes.
- **`users/`**: Gestión de perfiles de usuario y roles. Soporte para múltiples tipos de actores (Admin, Especialista, Paciente, Empresa).
- **`clinics/`**: Núcleo del multi-tenancy. Gestión de clínicas, sedes, especialidades, servicios y el sistema de **Suscripciones y Planes**.
- **`patients/`**: Base de datos de pacientes, perfiles clínicos y contacto.
- **`appointments/`**: Motor de agendamiento, gestión de disponibilidad de especialistas (AvailabilityBlocks) y flujo de validación de pagos.
- **`companies/`**: Portal B2B. Convenios, empresas, nómina de empleados y autenticación corporativa.
- **`clinical_records/`**: Historia clínica detallada, diagnósticos y seguimientos.
- **`psychological_tests/`**: Sistema de evaluaciones psicológicas. Dimensiones, preguntas, opciones, baremos y calificación automática.
- **`medical_results/`**: Resultados de laboratorio e imágenes vinculados a citas.
- **`discounts/`**: Motor de beneficios. Lógica unificada para aplicar descuentos corporativos o promociones generales.

## 2. Flujo de Datos Multi-tenant
- **Middleware de Clínica**: Todo request es interceptado para identificar la clínica activa via subdominio o header.
- **Aislamiento a nivel de QuerySet**: Los `ViewSets` filtran automáticamente por el ID de la clínica actual, previniendo fugas de datos.

## 3. Integración B2B y Salud Ocupacional
- El sistema utiliza llaves foráneas en `Appointment` hacia `Company` y `Agreement` para rastrear qué compañía financia cada servicio, permitiendo el filtrado de privacidad en los módulos de resultados.
