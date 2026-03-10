# 🏥 Requerimiento Funcional: Catálogo de Servicios Médicos
Este módulo gestiona la definición y configuración de los servicios médicos que ofrece la clínica.
- Su objetivo es permitir que la clínica pueda:
    - definir los tipos de servicios médicos disponibles
    - establecer la duración y características operativas de cada servicio
    - registrar requerimientos clínicos o logísticos necesarios para su realización
    - centralizar las reglas operativas asociadas a cada servicio.
- El catálogo de servicios funciona como una biblioteca institucional, desde la cual los especialistas pueden ser habilitados para brindar determinados servicios dentro de la clínica.
- Este enfoque permite mantener una arquitectura desacoplada entre:
    - la definición del servicio
    - los especialistas que lo realizan
    - la agenda donde se programan las citas.

## 1. Registro de Servicios Médicos
- **Descripción**
    - El sistema debe permitir registrar los distintos servicios médicos que ofrece la clínica.
    - Los servicios representan el tipo de atención que puede ser agendada para un paciente.
    - Ejemplos de servicios:
        - consulta médica general
        - consulta psicológica
        - terapia de pareja
        - terapia grupal
        - evaluación ocupacional
        - control nutricional.
    - El registro de servicios puede ser realizado por:
        - personal administrativo autorizado
        - responsables de gestión médica
        - administradores del sistema.
- **Información básica del servicio**
    - El sistema debe permitir registrar la siguiente información:
    - Ejemplo de categorías:
        - medicina general
        - psicología
        - fisioterapia
        - nutrición
        - laboratorio
        - diagnóstico por imágenes.
- **Estado del servicio**
    - El sistema debe permitir gestionar el estado del servicio dentro del catálogo.
    - Ejemplo:
        - activo
        - inactivo.
    - Cuando un servicio se encuentra inactivo:
        - no podrá ser utilizado para nuevas citas
        - pero su historial debe conservarse.

## 2. Configuración de Duración del Servicio
- **Descripción**
    - Cada servicio debe tener una duración base definida que será utilizada como referencia para la generación de espacios en la agenda médica.
    - Esta duración representa el tiempo estándar de atención para ese servicio.
    - Ejemplo:
        - Servicio: Consulta psicológica
        - Duración base: 50 minutos
        - Buffer sugerido entre citas: 5 minutos
    - El buffer permite que el especialista pueda:
        - registrar información clínica
        - preparar el consultorio
        - revisar documentación del paciente
        - evitar retrasos acumulados en la agenda.
    - Ejemplo:
        - Consulta médica
        - Duración base: 20 minutos
        - Buffer sugerido: 5 minutos
- Tiempo total bloqueado en agenda: 25 minutos
- El buffer definido en el servicio puede ser ajustado posteriormente en la agenda del especialista si la clínica lo requiere.

## 3. Capacidad de Atención del Servicio
- **Descripción**
    - Algunos servicios permiten atender más de un paciente simultáneamente.
    - Por esta razón, el sistema debe permitir definir la capacidad máxima de pacientes que pueden participar en una misma cita.
    - Ejemplos:
        - Consulta individual
        - Capacidad: 1 paciente
        - Terapia de pareja
        - Capacidad: 2 pacientes
        - Terapia grupal
        - Capacidad: múltiples pacientes.
    - La capacidad del servicio será utilizada por el módulo de agenda para determinar cuántos pacientes pueden reservar el mismo espacio de atención.

## 4. Preparación Previa del Paciente
- **Descripción**
    - Algunos servicios requieren que el paciente realice ciertas acciones antes de asistir a la cita.
    - El sistema debe permitir registrar instrucciones que serán comunicadas al paciente durante el proceso de agendamiento.
    - Ejemplos de preparación previa:
        - asistir en ayunas
        - suspender medicamentos específicos
        - acudir con acompañante
        - traer estudios médicos previos    
        - completar formularios previos a la consulta.
    - Estas instrucciones podrán mostrarse en:
        - el portal del paciente
        - correos de confirmación de cita
        - recordatorios automáticos.

## 5. Consentimientos Asociados al Servicio
- **Descripción**
    - Determinados servicios pueden requerir la aceptación de consentimientos informados antes de su realización.
    - El sistema debe permitir asociar documentos de consentimiento a servicios específicos para garantizar el cumplimiento de los requisitos legales.
    - Ejemplos:
        - consentimiento para atención psicológica
        - consentimiento para procedimientos médicos
        - consentimiento para evaluaciones ocupacionales.
    - El consentimiento podrá ser:
        - firmado digitalmente
        - aceptado durante el proceso de agendamiento
        - registrado manualmente por el personal administrativo.

## 6. Requerimientos de Recursos
- **Descripción**
    - Algunos servicios requieren el uso de equipos o recursos clínicos específicos.
    - El sistema debe permitir registrar estos requerimientos para evitar que el servicio sea programado cuando el recurso necesario no se encuentra disponible.
    - Ejemplos de recursos:
        - ecógrafo
        - equipo de rayos X
        - camilla de fisioterapia
        - sala de procedimientos.
    - El módulo de agenda deberá validar la disponibilidad de estos recursos antes de confirmar una cita.

## 7. Reglas Operativas del Servicio
- **Descripción**
    - El sistema debe permitir definir reglas operativas que regulen la gestión de citas asociadas a cada servicio.
    - Estas reglas permiten adaptar el comportamiento del sistema a las necesidades específicas de cada tipo de atención.
- **Ventana de cancelación**
    - El sistema debe permitir definir el tiempo mínimo requerido para cancelar o modificar una cita sin penalidades.
    - Ejemplo:
        - Consulta médica
        - Cancelación permitida hasta: 2 horas antes
        - Consulta psicológica
        - Cancelación permitida hasta: 12 horas antes
        - Procedimiento médico
        - Cancelación permitida hasta: 24 horas antes.
    - Estas reglas serán utilizadas por el módulo de agenda y citas para validar solicitudes de modificación o cancelación.

## 8. Integración con Especialistas
- **Descripción**
    - El catálogo de servicios no define qué especialistas realizan cada servicio.
    - La asignación de especialistas se gestiona en el módulo de Gestión de Especialistas.
    - Un especialista puede estar habilitado para uno o varios servicios del catálogo.
    - Ejemplo:
        - Dr. Pérez
        - Servicios habilitados:
            - consulta médica
            - control cardiovascular.
    - Esta relación permite que el sistema determine qué servicios pueden agendarse con cada especialista.

## 9. Integración con el Módulo de Agenda
- **Descripción**
    - El módulo de agenda utilizará la información del catálogo de servicios para generar los espacios de atención disponibles.
    - Entre los datos utilizados se encuentran:
        - duración base del servicio
        - buffer entre citas
        - capacidad del servicio
        - requerimientos de recursos
        - reglas de cancelación.
- Esta integración permite que la agenda médica pueda operar con base en reglas configurables definidas por la clínica.

# 📌 Nota de Arquitectura
- El catálogo de servicios actúa como una configuración central del sistema clínico.
- Separar la definición del servicio de la asignación a especialistas permite:
    - mantener consistencia en la configuración
    - evitar duplicación de información
    - simplificar la administración del sistema.
- Los especialistas pueden habilitarse para brindar servicios definidos en este catálogo sin modificar la configuración original del servicio.