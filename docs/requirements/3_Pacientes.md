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

## 2. Identificador Clínico del Paciente
- **Descripción:**
    - Cada paciente registrado dentro de una clínica debe poseer un identificador clínico único generado por el sistema.
    - Este identificador permite:
        - identificar pacientes incluso cuando no poseen documento de identidad
        - evitar conflictos entre pacientes con nombres similares
        - permitir operaciones internas del sistema sin depender de datos personales.
    - Características del identificador:
        - es único dentro de la clínica
        - es generado automáticamente por el sistema
    - no cambia durante el ciclo de vida del paciente

## 3. Prevención de Registros Duplicados
- **Descripción:**
    - El sistema debe implementar mecanismos para prevenir la creación de registros duplicados de pacientes dentro de la misma clínica.
- **Estrategias de detección:**
    - Antes de crear un nuevo paciente, el sistema debe verificar posibles coincidencias utilizando combinaciones de:
        - documento de identidad
        - nombre completo
        - fecha de nacimiento
        - número telefónico.
- **Gestión de duplicados:**
    - Cuando el sistema detecte coincidencias potenciales, deberá:
        - advertir al usuario administrativo
        - permitir revisar registros existentes antes de crear uno nuevo.
    - Esto ayuda a mantener la integridad de la información clínica.

## 3. Separación entre Paciente y Usuario del Sistema
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

## 4. Gestión de Pacientes Dependientes
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
        - Cada paciente dependiente debe tener un responsable principal registrado en el sistema.
        - El sistema podrá permitir registrar responsables secundarios autorizados, dependiendo de las políticas de la clínica.
        - El responsable puede tener varios pacientes dependientes asociados.
        - El responsable puede ser:
            - padre
            - madre
            - tutor legal
            - representante autorizado.

## 5. Registro de Dependientes
- **Descripción:**
    - El sistema debe permitir registrar pacientes dependientes incluso si el responsable no está presente en ese momento.
    - Esto es necesario para situaciones como:
        - emergencias
        - derivaciones
        - atención inicial en clínicas.
    - En estos casos, el sistema permitirá crear al paciente con un estado especial.
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
El estado "Tutor pendiente de validación" representa la situación de la relación de tutela y no afecta la existencia del paciente dentro del sistema.

## 6. Validación de Tutela o Representación Legal
- **Descripción:**
    - Para formalizar la relación entre un responsable y un paciente dependiente, el sistema debe permitir registrar documentación de respaldo.
- **Flujo de validación:**
    - El sistema genera o permite descargar una plantilla de autorización o tutela.
    - El responsable firma el documento.
    - El documento es presentado en la clínica.
    - El personal administrativo valida la información.
    - El documento se registra en el sistema.
    - Una vez validado el documento, el estado del paciente cambia a: Tutor validado

## 7. Gestión de Pacientes con Discapacidad
- **Descripción:**
    - El sistema debe permitir que pacientes adultos con discapacidad puedan tener un responsable que gestione su atención médica.
- **Funcionamiento:**
    - El funcionamiento es equivalente al de los pacientes menores de edad:
        - existe un responsable registrado
        - el responsable puede gestionar citas y autorizaciones
    - la relación debe estar respaldada por documentación válida.

## 8. Independencia del Paciente al Alcanzar la Mayoría de Edad
- **Descripción:**
    - Cuando un paciente dependiente alcanza la mayoría de edad, el sistema debe permitir que este pueda gestionar su propia cuenta digital si lo desea.
- **Flujo de independencia:**
    - El paciente puede crear voluntariamente su cuenta de usuario.
    - El sistema vincula la cuenta con su historial clínico existente.
    - El historial médico se mantiene intacto.
    - La creación de la cuenta no es obligatoria.
    - El paciente puede continuar siendo atendido sin tener acceso digital.

## 9. Acceso del Responsable a la Información del Dependiente
- **Descripción:**
    - El responsable autorizado puede gestionar aspectos administrativos del paciente dependiente.
- **Restricciones:**
    - Sin embargo, el acceso a información clínica detallada dependerá de las políticas de privacidad definidas por la clínica.
    - Esto permite que cada institución establezca sus propias reglas sobre:
        - visualización de resultados
        - acceso a historia clínica
        - descarga de documentos.

## 10. Estados del Paciente
- **Descripción:**
    - El sistema debe permitir que cada paciente tenga un estado administrativo que represente su situación dentro de la clínica.
- **Estados posibles:**
    - Activo
        - Paciente habilitado para recibir atención médica y utilizar los servicios de la clínica.
    - Anonimizado
        - Paciente dependiente registrado sin documentación legal validada que respalde la relación con su responsable.
        - En este estado se permiten atenciones iniciales, pero se restringen ciertos procesos administrativos y accesos digitales.
    - Inactivo
        - Paciente que ya no recibe atención activa en la clínica, pero cuyos registros deben mantenerse por razones médicas, legales o administrativas.
    - Bloqueado
        - Paciente cuyo registro se encuentra temporalmente restringido debido a situaciones administrativas o legales definidas por la clínica.

## 11. Consentimiento Informado del Paciente
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

## 12. Configuración de Datos Obligatorios del Paciente
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

## 13. Registro de Pacientes mediante Convenios Empresariales (B2B)
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
## 14. Red de Contactos de Emergencia (Contactos de Confianza)
- **Descripción:**
    - El sistema debe permitir la gestión de personas de contacto para situaciones críticas.
- **Lógica de Registro:**
    - Para Menores de Edad/Dependientes: El responsable legal se registra automáticamente como el primer contacto de emergencia.
    - Para Adultos Independientes: Es obligatorio registrar al menos un (1) contacto durante el completado del perfil.
- **Capacidad:**
    - El sistema permitirá añadir contactos adicionales opcionales.
- **Datos requeridos:**
    - Nombre completo, parentesco (vínculo) y número telefónico activo.
- **Visualización Crítica:**
    - Este dato debe ser accesible mediante un "Acceso Rápido" en la ficha del paciente, permitiendo que el especialista lo vea sin necesidad de navegar profundamente en la historia clínica.

## 15. Gestión de Vínculos Familiares
- **Descripción:**
    - El sistema debe permitir registrar relaciones familiares entre pacientes registrados dentro de la clínica.
- Este mecanismo permite representar relaciones familiares que no necesariamente implican tutela legal, pero que pueden ser relevantes para:
    - beneficios familiares
    - convenios institucionales extensibles
    - contacto médico
    - historial familiar relevante
    - gestión administrativa.
- Esta relación es distinta de la relación Responsable → Dependiente, ya que esta última representa una tutela legal o administrativa, mientras que los vínculos familiares representan relaciones personales o familiares entre pacientes.
- **Tipos de vínculos**
    - El sistema debe permitir registrar distintos tipos de relación familiar entre pacientes.
    - Ejemplos:
        - padre
        - madre
        - hijo
        - cónyuge
        - tutor (apoderado) legal
- **Estructura de la relación**
    - Cada vínculo familiar debe incluir:
        - paciente origen
        - paciente relacionado
        - tipo de relación
        - estado de la relación
        - fecha de registro
- **Reglas de funcionamiento**
    - Un paciente puede tener múltiples vínculos familiares registrados.
    - Un vínculo familiar no implica automáticamente autorización médica o legal.
    - La clínica puede utilizar esta información para:
        - aplicar beneficios familiares
        - registrar antecedentes familiares
        - facilitar procesos administrativos.
- **Uso en beneficios del sistema**
    - Los vínculos familiares pueden ser utilizados por otros módulos del sistema para extender beneficios.
- **Ejemplo:**
    - Convenio Universidad X
    - Extensible a familiares directos
    - Si el paciente titular tiene el convenio, el sistema podrá validar si otro paciente vinculado cumple con la relación familiar requerida.
- **Tipos de herencia de beneficios**
    - El sistema debe permitir definir cómo se heredan los beneficios familiares.
- **Opciones posibles:**
    - Titular → dependientes
    - Ejemplo:
        - Padre tiene convenio
        - Hijo puede usarlo
    - Bidireccional
    - Ejemplo:
        - Si el hijo tiene beneficio
        - el padre también puede usarlo
- La clínica podrá definir la política de herencia según sus reglas administrativas.

## 16. Política de Retención y Anonimización (Cumplimiento LPDP)
- **Descripción:**
    - Gestión del ciclo de vida de los datos personales frente a la obligatoriedad de la Historia Clínica (HC).
- **Estado: Anonimizado (Derecho al Olvido):**
    - Cuando un paciente ejerce su derecho al olvido, el sistema no elimina el registro médico (HC), pero aplica un proceso de "borrado irreversible" de datos identificables (DNI, Nombres, Correo, Teléfono, Dirección).
    - El registro clínico permanece vinculado a un ID interno alfanumérico para fines de auditoría legal y estadística de la clínica.
- **Plazo de Custodia:**
    - El sistema debe permitir configurar el tiempo de retención (ej. 15 años) tras el cual el registro anonimizado puede ser eliminado definitivamente de la base de datos de la clínica.

## 17. Auditoría de Visualización (Read-Only Audit)
- **Descripción:**
    - Registro obligatorio de cada "evento de lectura" de información sensible.
- **Funcionamiento:**
    - El ClinicalAuditSystem debe disparar un registro de auditoría cada vez que un usuario abra la ficha de un paciente, consulte una nota evolutiva o descargue un resultado, aunque no realice cambios.
- **Datos del Log:**
    - Debe incluir Usuario, Rol Activo, Paciente Consultado, Módulo Consultado (ej. Historia Clínica, Laboratorio) y Timestamp exacto.
- **Reporte de Intrusión:**
    - El sistema debe facilitar reportes de "Accesos Inusuales" (ej. un personal administrativo consultando muchas historias clínicas en poco tiempo).

## 18. Control de Vigencia de Consentimientos (Versionado)
- **Descripción:**
    - Mecanismo para asegurar que el paciente siempre esté bajo el marco legal más reciente de la clínica.
- **Lógica de Versionado:**
    - Cada documento de consentimiento (Términos y Condiciones, Protección de Datos, Consentimiento Clínico) tendrá un número de versión (ej. v1.0, v2.1).
- **Bloqueo por Desactualización:**
    - Cuando la clínica actualice un documento a una nueva versión "Mayor", el sistema debe detectar que el consentimiento del paciente es "Antiguo" (Stale).
- **Interrupción de Flujo:**
    - Al intentar agendar una cita o ingresar al portal, el sistema presentará automáticamente la nueva versión para su firma/aceptación, bloqueando el acceso hasta que se formalice la actualización.