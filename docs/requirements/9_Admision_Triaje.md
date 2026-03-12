# 🏥 Módulo de Admisión y Triaje
- **Descripción General**
    - Este módulo gestiona el proceso de llegada del paciente el día de la cita, validando su identidad, verificando pagos o autorizaciones, registrando consentimientos y determinando si debe pasar por triaje antes de la consulta médica.
    - El módulo se divide en dos componentes principales:
        - Admisión (proceso administrativo)
        - Triaje (proceso clínico opcional)
    - Esto permite que el sistema sea flexible y se adapte a diferentes tipos de atención médica.
    
## 1.Proceso de Check-in (Admisión)
- El check-in representa el punto de entrada del paciente a la clínica el día de su cita.
- El personal de recepción identifica la cita del paciente en la agenda y valida su estado antes de permitir el acceso a la zona clínica.
    
- **1.1 Validación de Identidad**
    - El sistema debe permitir verificar la identidad del paciente mediante:
        - DNI
        - Pasaporte
        - Documento de identidad equivalente    
    - Si el paciente pertenece a una empresa (modelo B2B), el sistema debe validar:
        - empresa
        - protocolo asignado
        - tipo de evaluación ocupacional
    - Esto garantiza que el paciente esté autorizado para realizar los exámenes programados.

- **1.2 Gestión de Pagos**
    - Durante la admisión el sistema debe verificar el estado de pago de la cita.
    
    - **Caso 1: Cita pendiente de pago**
        - Si la cita tiene estado:
            - Reserva pendiente de pago
        - El sistema debe bloquear el ingreso a la zona clínica hasta que ocurra una de las siguientes acciones:
            - registro de pago
            - autorización de seguro
            - validación de convenio
    
    - **Caso 2: Cita ya pagada**
        - Si el pago ya fue registrado previamente (por web o caja), el sistema debe cambiar el estado de la cita a:
            - Confirmado en recepción
- **1.3 Gestión de Consentimientos**
    - Antes de continuar con el flujo clínico, el sistema debe permitir registrar la aceptación de documentos legales.
    - Ejemplos:
        - consentimiento informado
        - política de privacidad de datos
        - autorización de tratamiento médico
    - El sistema puede registrar la aceptación mediante:
        - firma digital
        - firma en tablet
        - confirmación electrónica

## 2. Configuración de Triaje por Servicio
- No todos los servicios requieren triaje previo.
- Por esta razón, el sistema debe permitir configurar esta condición en el catálogo de servicios médicos.
- **Campo de configuración en servicios**
    - En el catálogo de servicios debe existir el campo:
        - Requiere triaje (Sí / No)
    - Ejemplo de configuración
        - Medicina General → Sí requiere triaje
        - Cardiología → Sí requiere triaje
        - Psicoterapia → No requiere triaje
        - Teleconsulta → No requiere triaje

- **Comportamiento del sistema**
    - Dependiendo de esta configuración:
        - Si el servicio requiere triaje
            - Después de la admisión el paciente pasa al estado:
                - En espera de triaje
        - Si el servicio NO requiere triaje
            - El sistema envía al paciente directamente a:
                - Sala de espera del médico

## 3. Monitor de Triaje (Cola de Espera)

- El personal de enfermería o técnicos debe contar con una bandeja de pacientes pendientes de triaje.
- Esta bandeja muestra los pacientes que ya completaron el proceso de admisión.
- Información visible en la bandeja
    - Nombre del paciente
    - Edad
    - Servicio solicitado
    - Especialista
    - Hora de cita
    - Tiempo de espera
- Esto permite priorizar pacientes cuando existe alta demanda.

## 4. Registro de Signos Vitales (Formulario de Triaje)
- Durante el triaje se registra información clínica básica antes de la consulta.
- Datos registrados
    - Presión arterial
    - Frecuencia cardíaca
    - Saturación de oxígeno
    - Temperatura corporal
    - Datos antropométricos
    - Peso
    - Talla
    - Índice de masa corporal (IMC)
- El sistema debe calcular automáticamente el IMC.
- Información adicional relevante
    - El formulario también debe permitir registrar:
        - alergias
        - observaciones clínicas
        - síntomas reportados
- Si se registran alergias, el sistema debe generar una alerta visible para el médico.

## 5. Gestión de Colas y Estados del Paciente
- El sistema debe actualizar en tiempo real el estado de la cita para que todo el personal sepa en qué etapa se encuentra el paciente.
- Estados del flujo
    - En recepción
    - En espera de triaje
    - En triaje
    - En sala de espera
    - En consulta
    - Atendido
- Flujo típico
    - Paciente llega
    ↓
    Recepción realiza check-in
    ↓
    Si requiere triaje → pasa a cola de triaje
    ↓
    Triaje registra signos vitales
    ↓
    Paciente pasa a sala de espera del médico
    ↓
    El médico lo llama a consulta

## 6. Check-in en Protocolos Ocupacionales
- En el modelo B2B (empresa-clínica), el proceso de admisión puede ser masivo.
- **Validación de protocolo**
    - Durante el check-in el sistema debe confirmar:
        - empresa del trabajador
        - protocolo ocupacional asignado
        - exámenes incluidos
- Esto evita que el trabajador realice evaluaciones que no correspondan a su contrato.

**Hoja de Ruta del Protocolo**
- El sistema debe poder generar una hoja de ruta que indique al trabajador los pasos que debe seguir.
- Ejemplo:
    - Laboratorio
    - Rayos X
    - Psicología
    - Triaje
    - Medicina ocupacional
- **Esta hoja puede:**
    - imprimirse
    - mostrarse en pantalla
    - enviarse por QR o aplicación móvil

## 7. Triaje Express (Realizado por el Médico)
- En algunos casos el triaje puede no haberse realizado antes de la consulta.
- **Por ejemplo:**
    - alta demanda en enfermería
    - consulta rápida
    - servicios específicos
- En estos casos el sistema debe permitir que el médico registre los signos vitales directamente desde el consultorio.
**Funcionamiento**
- Si el formulario de triaje no está registrado, el sistema debe permitir que el médico:
    - abra el formulario de triaje
    - registre signos vitales
    - continúe con la consulta
- Esto evita bloquear la atención cuando el flujo de enfermería está saturado.