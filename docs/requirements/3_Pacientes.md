# 👤 Requerimiento Funcional: Gestión de Pacientes y Dependientes
Este módulo gestiona la identidad clínica de las personas atendidas en el sistema.
- Su objetivo es permitir el registro flexible de pacientes, garantizar el cumplimiento legal en casos de tutela y permitir que las clínicas puedan operar incluso cuando el paciente no tenga una cuenta dentro de la plataforma.
- El sistema debe separar claramente los conceptos de Paciente y Usuario del sistema, permitiendo que una persona reciba atención médica sin necesidad de tener una cuenta digital.
- Este enfoque permite que el sistema funcione tanto en entornos presenciales como en escenarios digitales.

## 1. Registro de Pacientes
- **Descripción:**
    - El sistema debe permitir registrar pacientes con un conjunto mínimo de información, suficiente para identificarlos dentro de la clínica.
    - Este registro puede ser realizado por:
        - personal administrativo de la clínica
        - personal médico
        - el propio paciente mediante su portal
    - El registro inicial debe ser ligero y rápido, permitiendo que la atención médica no se vea retrasada por la falta de información completa.
- **Principios del registro**
    - El registro inicial del paciente no requiere completar toda su información personal.
    - La información faltante podrá completarse posteriormente:
        - por el propio paciente desde su portal
        - por el personal de la clínica durante una cita.
    - Cada clínica gestiona su propio conjunto de pacientes.
    - Un mismo individuo puede existir como paciente en múltiples clínicas, pero sus datos clínicos permanecen completamente aislados entre ellas.

## 2. Separación entre Paciente y Usuario del Sistema
- **Descripción:**
    - El sistema debe diferenciar claramente entre:
        - Paciente
            - Persona que recibe atención médica.
        - Usuario del sistema
            - Persona que posee credenciales para acceder al portal digital.
    - Esto permite que:
        - un paciente exista sin tener una cuenta digital
        - la clínica pueda registrar pacientes de forma presencial
        - el paciente decida voluntariamente si desea o no crear un usuario.
    - Reglas
        - El personal de la clínica no puede crear usuarios del sistema para los pacientes.
    - La creación de cuentas de usuario siempre debe ser realizada voluntariamente por el propio paciente.
    - Un paciente puede existir indefinidamente sin tener una cuenta digital.

## 3. Gestión de Pacientes Dependientes
- **Descripción:**
    - El sistema debe soportar pacientes que dependen de un responsable legal para la gestión de su atención médica.
    - Esto incluye:
        - menores de edad
        - adultos con discapacidad
        - pacientes que requieren representación legal.
    - En estos casos, el sistema debe establecer una relación entre el paciente dependiente y su responsable.
- **Responsable del Paciente**
    - El responsable es la persona autorizada para gestionar la atención del paciente dependiente.
    - Puede realizar acciones como:
        - agendar citas
        - autorizar procedimientos
        - firmar consentimientos
        - recibir información médica autorizada.
    - Reglas del responsable
        - Cada paciente dependiente debe tener un único responsable principal registrado en el sistema.
        - El responsable puede tener varios pacientes dependientes asociados.
        - El responsable puede ser:
            - padre
            - madre
            - tutor legal
            - representante autorizado.

## 4. Registro de Dependientes
- **Descripción:**
    - El sistema debe permitir registrar pacientes dependientes incluso si el responsable no está presente en ese momento.
    - Esto es necesario para situaciones como:
        - emergencias
        - derivaciones
        - atención inicial en clínicas.
    - En estos casos, el sistema permitirá crear al paciente con un estado especial.
    - Estado: Tutor Pendiente de Validación
        - Cuando un paciente dependiente se registra sin un responsable validado, el sistema marcará su registro como:
            - Tutor pendiente de validación
    - Esto permite que:
        - el paciente pueda ser atendido
        - se puedan registrar citas
        - se puedan generar registros clínicos iniciales.
    - Restricciones del estado pendiente:
        - el paciente no podrá acceder al portal digital
        - no se permitirá descargar resultados
        - no se permitirá compartir información médica
        - algunos procesos administrativos podrán estar restringidos.
    - Esto protege legalmente a la clínica hasta que se valide la representación legal.

## 5. Validación de Tutela o Representación Legal
- **Descripción:**
    - Para formalizar la relación entre un responsable y un paciente dependiente, el sistema debe permitir registrar documentación de respaldo.
- **Flujo de validación:**
    - El sistema genera o permite descargar una plantilla de autorización o tutela.
    - El responsable firma el documento.
    - El documento es presentado en la clínica.
    - El personal administrativo valida la información.
    - El documento se registra en el sistema.
    - Una vez validado el documento, el estado del paciente cambia a: Tutor validado

## 6. Gestión de Pacientes con Discapacidad
- **Descripción:**
    - El sistema debe permitir que pacientes adultos con discapacidad puedan tener un responsable que gestione su atención médica.
- **Funcionamiento:**
    - El funcionamiento es equivalente al de los pacientes menores de edad:
        - existe un responsable registrado
        - el responsable puede gestionar citas y autorizaciones
    - la relación debe estar respaldada por documentación válida.

## 7. Independencia del Paciente al Alcanzar la Mayoría de Edad
- **Descripción:**
    - Cuando un paciente dependiente alcanza la mayoría de edad, el sistema debe permitir que este pueda gestionar su propia cuenta digital si lo desea.
- **Flujo de independencia:**
    - El paciente puede crear voluntariamente su cuenta de usuario.
    - El sistema vincula la cuenta con su historial clínico existente.
    - El historial médico se mantiene intacto.
    - La creación de la cuenta no es obligatoria.
    - El paciente puede continuar siendo atendido sin tener acceso digital.

## 8. Acceso del Responsable a la Información del Dependiente
- **Descripción:**
    - El responsable autorizado puede gestionar aspectos administrativos del paciente dependiente.
- **Restricciones:**
    - Sin embargo, el acceso a información clínica detallada dependerá de las políticas de privacidad definidas por la clínica.
    - Esto permite que cada institución establezca sus propias reglas sobre:
        - visualización de resultados
        - acceso a historia clínica
        - descarga de documentos.

## 9. Estados del Paciente
- **Descripción:**
    - El sistema debe permitir que cada paciente tenga un estado administrativo que represente su situación dentro de la clínica.
- **Estados posibles:**
    - Activo
        - Paciente habilitado para recibir atención médica y utilizar los servicios de la clínica.
    - Tutor Pendiente de Validación
        - Paciente dependiente registrado sin documentación legal validada que respalde la relación con su responsable.
        - En este estado se permiten atenciones iniciales, pero se restringen ciertos procesos administrativos y accesos digitales.
    - Inactivo
        - Paciente que ya no recibe atención activa en la clínica, pero cuyos registros deben mantenerse por razones médicas, legales o administrativas.
    - Bloqueado
        - Paciente cuyo registro se encuentra temporalmente restringido debido a situaciones administrativas o legales definidas por la clínica.

## 10. Consentimiento Informado del Paciente
- **Descripción:**
    - El sistema debe permitir registrar la aceptación de documentos de consentimiento informado por parte del paciente o su responsable legal.
    - Este proceso es necesario para cumplir con las normativas de protección de datos personales y regulaciones de atención médica.
- **Alcance del consentimiento:**
    - Los consentimientos pueden incluir:
        - autorización para tratamiento médico
        - consentimiento para atención psicológica
        - autorización para el tratamiento de datos personales
        - consentimiento para evaluaciones ocupacionales. 
- **Registro del consentimiento:**
    - El consentimiento puede registrarse mediante:
        - aceptación digital dentro del portal del paciente
        - documento físico firmado y validado por la clínica.
- **El sistema debe almacenar el registro de:**
    - fecha de aceptación
    - versión del documento aceptado
    - identidad del paciente o responsable que otorgó el consentimiento.

## 11. Configuración de Datos Obligatorios del Paciente
- **Descripción:**
    - Cada clínica podrá definir qué información es obligatoria para completar el perfil del paciente dentro de su institución.
    - Esto permite adaptar el sistema a diferentes políticas administrativas y regulatorias.
- **Ejemplos de información configurable:**
    - Las clínicas podrán definir como obligatorios campos como:
        - dirección
        - número telefónico
        - correo electrónico
        - contacto de emergencia
        - documento de identidad.
- **Restricciones operativas:**
    - Si un paciente no cumple con los campos obligatorios definidos por la clínica, el sistema podrá restringir ciertos procesos como:
        - agendamiento de citas   
        - generación de documentos
        - acceso a determinados servicios administrativos.

## 12. Registro de Pacientes mediante Convenios Empresariales (B2B)
- **Descripción:**
    - El sistema debe permitir registrar pacientes provenientes de convenios empresariales o evaluaciones ocupacionales.
    - En estos escenarios, las empresas pueden proporcionar listas de trabajadores que deben ser evaluados por la clínica.
- **Flujo de registro:**
    - La empresa puede enviar una lista de trabajadores mediante carga masiva de datos (por ejemplo, archivo Excel).
- **El sistema deberá:**
    - registrar automáticamente a los trabajadores que no existan como pacientes
    - reutilizar el registro existente si el trabajador ya está registrado en la clínica.
- **Reglas de registro:**
    - Los pacientes creados mediante este mecanismo:
        - no tendrán automáticamente una cuenta de usuario
        - podrán crear su cuenta digital voluntariamente si lo desean.
- **Restricciones de acceso empresarial:**
    - Las empresas no tendrán acceso a información clínica sensible de los trabajadores.
    - El acceso empresarial estará limitado únicamente a la información autorizada dentro del convenio, como:
        - estado de evaluación
        - aptitud ocupacional
        - resultados autorizados.   