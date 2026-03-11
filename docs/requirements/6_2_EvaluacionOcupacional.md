# 📋 Requerimiento Funcional: Modelo de Evaluación Ocupacional
Este módulo gestiona el proceso de atención integral del trabajador, desde que se inicia su evaluación hasta la emisión del certificado de aptitud.
- Su objetivo es:
    - consolidar todos los resultados de los servicios incluidos en un protocolo
    - gestionar los estados de avance de la evaluación
    - permitir al médico ocupacional dictaminar la aptitud final
    - actuar como registro histórico de la salud ocupacional del trabajador.
- La evaluación ocupacional representa la instancia clínica que agrupa todos los exámenes realizados dentro de un protocolo.

## 1. Apertura de la Evaluación
- **Descripción**
    - Cuando un trabajador llega a la clínica o se agenda su evaluación corporativa, el sistema debe crear una instancia de Evaluación Ocupacional.
    - Esta evaluación funcionará como el contenedor que agrupa todos los exámenes que el trabajador debe realizar según el protocolo asignado.
- **Vínculos obligatorios**
    - Toda evaluación debe estar asociada a:
        - un trabajador o paciente
        - una empresa cliente (B2B)
        - un protocolo médico específico
        - la versión del protocolo vigente al momento de la evaluación.
- Esto garantiza que el sistema pueda mantener un registro histórico correcto de los exámenes realizados.

- **Identificador único**
    - Cada evaluación ocupacional debe contar con un ID único de evaluación, que permita realizar seguimiento del proceso para fines administrativos, clínicos y de auditoría.
- **Información básica de la evaluación**
    - El sistema debe registrar:
        - fecha de inicio de evaluación
        - tipo de evaluación
        - usuario que registró la evaluación
        - empresa solicitante
        - protocolo asignado.
- **Tipo de evaluación**
    - El sistema debe permitir clasificar la evaluación según su finalidad.
    - Ejemplos:
        - evaluación de ingreso
        - evaluación periódica
        - evaluación de retiro
        - evaluación de reincorporación.
- Esta clasificación permitirá generar reportes clínicos y laborales.

## 2. Gestión de Estados de la Evaluación
- **Descripción**
    - Para permitir el seguimiento del proceso de evaluación, el sistema debe gestionar distintos estados.
- **Estados principales**
    - La evaluación puede pasar por los siguientes estados:
        - Iniciada
            - El trabajador ha sido registrado en el sistema, pero aún no ha iniciado ningún examen.
        - En proceso
            - El trabajador ya ha iniciado uno o más exámenes del protocolo.
        - Pendiente de resultados
            - Todos los exámenes físicos han sido realizados, pero falta registrar resultados de laboratorio o exámenes externos.
        - Observada
            - El médico o especialista identifica la necesidad de realizar exámenes adicionales o interconsultas antes de emitir la aptitud.
        - Completada / Cerrada
            - El médico ocupacional ha realizado el servicio de cierre y ha emitido el dictamen final de aptitud.
- **Estados adicionales para manejo operativo**
    - El sistema debe contemplar situaciones donde la evaluación no se completa.
        - Cancelada
            - La evaluación fue interrumpida por razones administrativas.
        - Ejemplos:
            - el trabajador no asistió a las citas
            - la empresa canceló la solicitud
            - el trabajador desistió del proceso.
        - Expirada / No finalizada
            Si una evaluación permanece incompleta durante un periodo prolongado (por ejemplo, 30 días), el sistema puede marcarla automáticamente como expirada.
            Esto evita mantener evaluaciones abiertas indefinidamente.

## 3. Consolidación de Resultados (Tracking de Servicios)
- La evaluación ocupacional funciona como un contenedor de los servicios incluidos en el protocolo.
- El sistema debe mostrar una lista de control con todos los exámenes requeridos.
- **Información registrada por servicio**
    - Para cada servicio realizado el sistema debe permitir visualizar:
        - nombre del servicio
        - especialista o profesional que lo realizó
        - fecha y hora de atención
        - estado del servicio
        - Resultado registrado
        - enlace al informe clínico o nota médica correspondiente.
- **Estados de cada servicio**
    - Cada servicio puede tener estados como:
        - pendiente
        - en proceso
        - completado
        - observado.
- **Validación de integridad**
    - El sistema no debe permitir cerrar una evaluación si existe algún servicio obligatorio del protocolo marcado como pendiente.

## 4. Dictamen de Aptitud y Cierre de Evaluación
- El cierre de la evaluación solo puede ser realizado por el médico ocupacional responsable.
- Este cierre corresponde al servicio definido como servicio de cierre dentro del protocolo.
- **Registro de aptitud**
    - El médico ocupacional debe seleccionar el resultado final de la evaluación.
    - Opciones posibles:
        - apto
        - apto con restricciones
        - no apto
        - observado.
- **Restricciones laborales**
    - Cuando el resultado sea apto con restricciones, el sistema debe permitir registrar restricciones laborales.
    - Ejemplos:
        - no levantar peso mayor a 10 kg
        - evitar exposición a ruido elevado
        - evitar trabajo nocturno.
- Estas restricciones pueden ser visibles para la empresa, sin revelar diagnósticos médicos.
- **Vigencia de la evaluación**
    - El médico debe poder definir la vigencia de la evaluación ocupacional.
    - Ejemplo:
        - Evaluación válida por:
            - 1 año
            - 2 años.
    - El sistema debe registrar la fecha de vencimiento de la evaluación.
- **Recomendaciones médicas**
    - El sistema debe permitir registrar recomendaciones para la empresa o el trabajador.
    - Estas recomendaciones no deben revelar información clínica confidencial.
- **Firma del médico**
    - El cierre de la evaluación debe quedar registrado mediante:
        - firma electrónica o digital del médico responsable
        - fecha y hora de cierre.
    - Esto otorga validez legal al dictamen.

## 5. Generación de Documentos

- Una vez cerrada la evaluación, el sistema debe generar automáticamente los documentos correspondientes.
- **Certificado de aptitud laboral**
    - Documento dirigido a la empresa que indica el resultado de la evaluación ocupacional.
    - Este documento puede incluir:
        - estado de aptitud
        - restricciones laborales
        - vigencia del certificado.
- **Informe para el trabajador**
    - Documento detallado con los resultados de los exámenes realizados.
    - Este documento es entregado al trabajador y puede incluir información clínica más completa.
- **Notificación a la empresa**
    - Una vez generado el certificado, el sistema debe notificar al Portal B2B que el documento se encuentra disponible para descarga.

## 6. Reapertura de Evaluación
- El sistema debe permitir reabrir una evaluación en casos específicos.
- Esto puede ocurrir cuando:
    - el trabajador presenta resultados adicionales
    - se completan exámenes pendientes
    - se requiere reevaluación médica.
- La reapertura debe quedar registrada en el historial de auditoría.

## 7. Trazabilidad y Auditoría

- El sistema debe mantener un registro completo de las acciones realizadas durante la evaluación.
- Esto es necesario para auditorías médicas, legales y laborales.
- **Información auditada**
    - El sistema debe registrar:
        - usuario que creó la evaluación
        - usuario que registró cada resultado
        - especialista responsable de cada examen
        - médico que cerró la evaluación
        - fechas y horas de cada acción.

## 8. Nota de Arquitectura

### Cierre de Cita vs Cierre de Evaluación
- El sistema debe diferenciar entre dos niveles de cierre.

### Cierre de cita
- Cada especialista puede cerrar la cita correspondiente a su examen.
- Ejemplo:
    - el psicólogo termina la entrevista
    - el técnico registra el resultado de audiometría.

### Cierre de evaluación
- Solo el médico ocupacional puede cerrar la evaluación completa.
- Este cierre es el que genera:
    - el dictamen de aptitud
    - el certificado ocupacional.