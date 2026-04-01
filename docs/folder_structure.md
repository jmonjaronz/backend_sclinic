# Estructura de Carpetas - SCLINIC

El proyecto SCLINIC sigue una arquitectura **orientada a dominios**, donde cada funcionalidad principal reside en su propia aplicación Django. Esto facilita el mantenimiento y la escalabilidad del sistema SaaS.

## 📂 Directorios de Aplicación

### 🛡️ `core/`
- Configuraciones globales de Django, middleware multi-tenant y utilidades compartidas.

### 👤 `users/`
- Gestión de identidad, roles y soporte para **Firmas Digitales** de especialistas.

### 🏥 `clinics/`
- El corazón del SaaS. Gestión de clínicas, sedes, servicios y planes de suscripción.

### 👥 `patients/`
- Gestión de pacientes y **Vínculos Familiares** (dependientes/tutores).

### 📅 `appointments/`
- Motor de agendamiento inteligente con **Soft Locks**, auditoría de cambios y disponibilidad compleja.

### 📑 `clinical_records/`
- Historia Clínica Electrónica (EMR) con validación por esquemas JSON, buscador **CIE-10/11** y alertas de alergias.

### 📝 `psychological_tests/`
- Motor de evaluaciones psicométricas, dimensiones y calificación basada en baremos.

### 🏢 `companies/`
- Portal B2B, gestión de convenios corporativos y captura de nómina.

### 🛡️ `insurances/`
- Gestión de compañías de seguros y cálculo automático de copagos y coaseguros.

### 🏭 `occupational_health/`
- Flujo de Salud Ocupacional: Hojas de ruta por protocolo y dictámenes de aptitud.

### 💰 `discounts/`
- Motor unificado de beneficios y promociones.

---

## 🛠️ Otros Archivos
- `docs/`: Documentación técnica y reglas de negocio.
- `manage.py`: Script de gestión de Django.
- `requirements.txt`: Dependencias del servidor.
- `.env`: Variables de entorno configurables.
