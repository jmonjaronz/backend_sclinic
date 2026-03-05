# Estructura de Carpetas - SCLINIC

El proyecto SCLINIC sigue una arquitectura **orientada a dominios**, donde cada funcionalidad principal reside en su propia aplicación Django. Esto facilita el mantenimiento y la escalabilidad del sistema SaaS.

## 📂 Directorios de Aplicación

### 🛡️ `core/`
Contenido base del proyecto.
- Configuraciones globales de Django (`settings.py`, `urls.py`).
- Middleware multi-tenant.
- Permisos globales (`IsSuperAdmin`).
- Utilidades compartidas (`utils/`).

### 👤 `users/`
Gestión de identidad y acceso.
- Modelos de Usuario personalizado (`AbstractUser`).
- Lógica de Roles (Admin, Psicólogo, Administrativo, Paciente, Empresa).
- Autenticación JWT.

### 🏥 `clinics/`
El corazón del SaaS multi-tenant.
- **Clínicas**: Entidad raíz que separa los datos.
- **Sedes (HQs)**: Ubicaciones físicas de cada clínica.
- **Servicios**: Catálogo de consultas, evaluaciones y talleres.
- **Planes de Suscripción**: Control de acceso para las clínicas cliente.

### 👥 `patients/`
Gestión de usuarios finales de salud.
- Datos personales y demográficos.
- Registro de dependientes/menores de edad.
- Vínculos de parentesco y tutores legales.
- Gestión de consentimientos informados.

### 📅 `appointments/`
Motor de agendamiento inteligente.
- Citas individuales y grupales.
- Gestión de disponibilidad física y virtual.
- Bloqueos de agenda (vacaciones, licencias, feriados).
- Estados de cita (Pendiente, Confirmada, Cancelada, Pagada).

### 📑 `clinical_records/`
Historia Clínica Electrónica (EMR).
- Evoluciones y notas de sesión.
- Seguimiento de objetivos terapéuticos.
- Materiales asignados y compromisos.
- Registro inmutable de cambios.

### 📝 `psychological_tests/`
Motor de evaluaciones psicométricas.
- Definición de tests, dimensiones y preguntas.
- Almacenamiento de respuestas y cálculo de resultados.
- Baremos y escalas de calificación automática.

### 🏢 `companies/`
Portal B2B (Bambu B2B).
- Gestión de empresas cliente.
- Nómina de empleados y validación de afiliación para descuentos.
- Planes corporativos específicos.

### 💰 `discounts/`
Lógica de beneficios y promociones.
- Motor de descuentos (Convenios, Familiar, Cliente Antiguo).
- Regla de aplicación del beneficio mayor.

---

## 🛠️ Otros Archivos
- `docs/`: Documentación técnica y reglas de negocio.
- `manage.py`: Script de gestión de Django.
- `requirements.txt`: Dependencias del servidor.
- `.env`: Variables de entorno (DB, Keys, etc.).
