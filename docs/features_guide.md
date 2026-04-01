# Guía de Funcionalidades - SCLINIC (ACTUALIZAR)

Resumen de las capacidades actuales de la plataforma.

## 🛡️ Núcleo SaaS
- **Dashboard SuperAdmin**: Métricas globales de facturación, uso de clínicas y pacientes.
- **Multitenancy**: Subdominios personalizados y aislamiento completo de datos.
- **Planes y Suscripciones**: Control de niveles de servicio (Básico, Premium, Pro).

## 🏢 Portal B2B (Empresas)
- **Carga Masiva de Nómina**: Importación desde Excel/CSV de empleados.
- **Gestión de Convenios**: Configuración de descuentos por empresa.
- **Salud Ocupacional**: Visibilidad selectiva de exámenes ocupacionales para el gestor de la empresa.
- **Salud Ocupacional**:
    - **Hoja de Ruta Automática**: Seguimiento de servicios pendientes por protocolo.
    - **Dictámenes Online**: Resultados de aptitud disponibles para el gestor de la empresa tras consentimiento del trabajador.

## 📅 Citas y Agendamiento
- **Agenda Web**: Reserva de citas por especialidad, servicio y sede.
- **Soft Lock**: Bloqueo preventivo de slots durante el proceso de reserva.
- **Control de Caja**: Validación manual de vouchers y pagos en efectivo.
- **Auditoría**: Historial íntegro de cada cita (AppointmentHistory).

## 📑 Historia Clínica Electrónica (HCE)
- **Validación por Especialidad**: Esquemas dinámicos para notas médicas.
- **Seguridad en Recetario**: Alertas automáticas por alergias del paciente.
- **Diagnósticos CIE-10**: Buscador integrado para codificación diagnóstica estándar.
- **Firmas Digitales**: Soporte para firma electrónica de especialistas.

## 🧠 Evaluaciones Psicológicas
- **Motor de Calificación**: Cálculo automático de resultados basado en baremos.
- **Baterías de Tests**: Agrupación de múltiples pruebas para agilizar la asignación.
- **Resultados Interactivos**: Interpretación clínica automatizada basada en rangos de puntaje.

## 🔬 Resultados Médicos e Imágenes
- **Gestión de Archivos**: Almacenamiento organizado de laboratorio y Rayos X.
- **Vinculación Directa**: Resultados asociados a la sesión médica donde fueron ordenados.

## 🚑 Servicios Médicos Avanzados
- **Gestión de Triaje**: Registro estructurado de signos vitales (presión, saturación, temperatura).
- **Seguimiento Obstétrico**: Controles prenatales con monitoreo fetal.
- **Control de Crecimiento (CRED)**: Seguimiento neonatal (peso, talla, perímetro cefálico).
- **Control de Camas**: Visualización de disponibilidad de camas y habitaciones por sede.
- **Hospitalización**: Seguimiento completo desde el ingreso hasta el alta médica.
- **Planes de Tratamiento**: Prescripciones y seguimiento de medicación continua.

## 🏥 Seguros y Convenios
- **Liquidación Automática**: Cálculo de copagos y coaseguros según plan de salud.
- **Múltiples Coberturas**: Soporte para aseguradoras (EPS) y convenios corporativos directos.

## 👤 Portal del Paciente
- **Resultados Online**: Consulta de historial clínico y evaluaciones desde la web.
- **Privacidad**: Filtros automáticos de confidencialidad para evaluaciones de contratación.
