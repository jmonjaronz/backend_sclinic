# Reglas de Negocio - SCLINIC (ACTUALIZAR)

Este documento detalla la lógica central que rige el comportamiento de la plataforma SCLINIC.

## 1. Multi-tenant SaaS
- **Aislamiento de Clínicas**: Cada clínica opera en su propio subdominio y sus datos (pacientes, citas, especialistas) son totalmente privados y aislados de otras clínicas.
- **Suscripciones**: Las clínicas deben tener una suscripción activa vinculada a un `SubscriptionPlan` para operar. Los planes definen límites de citas y especialistas.
- **Roles de Usuario**:
    - `SUPERADMIN`: Control global de clínicas, planes y métricas de plataforma.
    - `ADMIN_CLINIC`: Gestión total de una clínica específica.
    - `PSYCHOLOGIST / SPECIALIST`: Atención de pacientes y gestión de resultados.
    - `STAFF`: Personal administrativo para agendamiento y validación de pagos.
    - `PATIENT`: Acceso a citas y resultados propios.
    - `COMPANY`: Gestor de portal B2B para convenios corporativos.

## 2. Portal B2B y Salud Ocupacional
- **Autenticación Triple**: Los gestores de empresas se validan con RUC, Razón Social, Usuario y Contraseña.
- **Confidencialidad Médica**:
    - Las empresas **solamente** pueden visualizar resultados (médicos o psicológicos) de citas agendadas bajo un convenio B2B de su propia empresa.
    - El historial personal y privado del paciente es inaccesible para la empresa.
- **Regla de Ocultación**: Si un servicio está marcado como `is_confidential_to_patient` (ej: evaluaciones de pre-empleo), el paciente no podrá ver el resultado, aunque sea el sujeto de la evaluación.
- **Descuentos**: Los convenios corporativos tienen prioridad sobre descuentos generales si el paciente es reconocido como empleado de la empresa en convenio.

## 3. Citas, Reprogramaciones y Anulaciones
- **Validación de Pago**: Por defecto, las citas requieren validación de pago (voucher subido por la web) por parte del personal de `STAFF` antes de ser confirmadas.
- **Días de Anticipación**: Las clínicas configuran un mínimo de días de anticipación para el agendamiento web.
- **Reprogramaciones**:
    - Cada clínica define el límite máximo de reprogramaciones permitidas por cita (`max_reschedules_allowed`, por defecto 2).
    - El paciente debe reprogramar con una anticipación mínima definida por la clínica (`reschedule_notice_hours`, por defecto 24h).
- **Anulaciones**:
    - Las anulaciones por parte del paciente requieren un pre-aviso mínimo (`cancel_notice_hours`, por defecto 24h). El personal administrativo puede anular en cualquier momento.
    - Se registra obligatoriamente el motivo de la anulación y queda guardado en la auditoría.
- **Trazabilidad**: Todo cambio de estado, fecha u hora genera una entrada en el historial de la cita (`AppointmentHistory`) para auditoría.
- **Capacidad**: Algunos servicios (talleres, evaluaciones grupales) pueden tener una `max_capacity` mayor a 1.

## 4. Evaluaciones Psicológicas y Médicas
- **Tests**: Cada test pertenece a una batería. Los especialistas asignan estas baterías a los pacientes.
- **Vencimiento**: Los tests pueden tener un plazo de vencimiento (`valid_until`) para ser completados por el paciente.
- **Scoring Avanzado**: 
    - **Dimensiones**: El motor calcula puntajes independientes por cada área medida (ej: Ansiedad vs Depresión).
    - **Baremos**: Se aplican tablas de normas tanto al puntaje total como a los puntajes por dimensión.
    - **Automatización**: La interpretación clínica ("Normal", "Moderado", etc.) se genera al instante tras completar el test.

## 5. Emergencias y Hospitalización
- **Triaje / Signos Vitales**: 
    - Se registran de forma independiente a la nota médica.
    - Generan un histórico de biometría (Peso, Talla, IMC) y signos vitales (Presión, Temp, SatO2, etc.).
    - **Configuración de Clínica**: Si la clínica activa `requires_triage_before_appointment`, el médico no podrá guardar la nota de sesión si no existe un triaje previo para esa cita.
- **Controles Especializados**: 
    - **Gestantes**: Seguimiento de evolución fetal y materna (LPM, AU, Semanas).
    - **Niños (CRED)**: Monitoreo de crecimiento (PC, Peso, Talla), APGAR y alimentación.
- **Hospitalización**: 
    - Un paciente hospitalizado debe tener asignada una cama (`Bed`) específica.
    - El sistema marca la cama como ocupada automáticamente al registrar el ingreso y la libera al registrar el alta médica.
- **Tratamientos**: Los tratamientos médicos permiten el seguimiento de medicación y dosis en planes prolongados, independientes de las notas de sesión puntuales.
