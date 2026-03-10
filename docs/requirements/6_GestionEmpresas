# 🏢 Requerimiento Funcional: Gestión de Empresas (B2B)
Este módulo permite gestionar organizaciones que contratan servicios médicos para sus trabajadores o miembros.
- Su objetivo es permitir que la clínica pueda:
  - registrar empresas como clientes corporativos
  - gestionar convenios y condiciones comerciales
  - administrar usuarios autorizados de cada empresa
  - asociar trabajadores a la organización
  - gestionar protocolos de evaluación ocupacional
  - facilitar el agendamiento corporativo de servicios médicos.
- Este módulo permite que el sistema clínico opere bajo un modelo B2B (Business to Business), en el cual las empresas pueden contratar evaluaciones médicas, psicológicas u ocupacionales para su personal.

## 1. Registro de Empresas
- **Descripción**
  - El sistema debe permitir registrar organizaciones que contratan servicios médicos para sus trabajadores.
  - Las empresas registradas podrán:
    - gestionar trabajadores
    - contratar protocolos médicos
    - agendar evaluaciones
    - acceder a reportes corporativos.
  - El registro de empresas puede ser realizado por:
    - personal administrativo
    - personal comercial
    - administradores del sistema.
- **Información básica de la empresa**
  - El sistema debe permitir registrar la siguiente información:
    - RUC de la empresa
    - razón social
    - nombre comercial (opcional)
    - dirección legal
    - sector económico o rubro
    - teléfono de contacto
    - correo electrónico corporativo
    - estado de la empresa dentro del sistema
  - Ejemplo de estados:
    - activa
    - inactiva
    - suspendida.
  - Cuando una empresa se encuentra inactiva:
    - no podrá generar nuevas solicitudes
    - pero su historial se conservará.
- **Validación de RUC**
  - Durante el registro de una empresa, el sistema podrá validar el RUC mediante integración con servicios externos (puede ser manual o automático).
  - Ejemplo:
    - consulta automática a SUNAT
    - verificación de razón social asociada al RUC
  - Esto permitirá reducir errores en el registro de empresas.

## 2. Configuración Comercial de la Empresa
- **Descripción**
  - El sistema debe permitir configurar condiciones comerciales específicas para cada empresa cliente.
  - Esto permite adaptar el sistema a distintos modelos de facturación corporativa.
- **Tipo de facturación**
  - El sistema debe permitir definir la modalidad de pago utilizada por la empresa.
  - Ejemplo:
    - pago al contado
    - facturación a crédito.
- **Días de crédito**
  - Cuando la empresa utiliza facturación a crédito, el sistema debe permitir definir el número de días para el pago de las facturas.
  - Ejemplo:
    - 15 días
    - 30 días
    - 45 días.
- **Convenio o lista de precios**
  - El sistema debe permitir asociar a la empresa un convenio o lista de precios específica.
  - Esto permite aplicar tarifas diferenciadas a los servicios del catálogo médico.
  - Ejemplo:
    - Empresa: Constructora Andes
    - Convenio aplicado: Salud Ocupacional Minera.

## 3. Gestión de Usuarios de Empresa
- **Descripción**
  - Las empresas pueden tener usuarios autorizados que interactúan con el sistema para gestionar trabajadores o agendar servicios.
  - Estos usuarios pertenecen a la organización y operan a través del Portal de Empresa (Portal B2B).
- **Roles de usuario corporativo**
  - El sistema debe permitir definir distintos roles para los usuarios de la empresa.
  - **Administrador de empresa (RRHH)**
    - Puede:
      - registrar trabajadores
      - subir listas masivas de trabajadores
      - solicitar evaluaciones médicas
      - agendar citas corporativas
      - consultar el estado de evaluaciones.
    - Este rol no tiene acceso a información clínica detallada.
  - **Médico o psicólogo ocupacional de la empresa**
    - Puede:
      - consultar resultados ocupacionales autorizados
      - revisar certificados de aptitud laboral
      - acceder a reportes agregados de salud laboral.
    - Este rol solo puede acceder a la información permitida por normativa laboral.

## 4. Gestión de Trabajadores de Empresa
- **Descripción**
  - El sistema debe permitir registrar a los trabajadores asociados a una empresa.
  - Los trabajadores registrados pueden posteriormente ser evaluados mediante protocolos médicos.
- **Información básica del trabajador**
  - El sistema debe permitir registrar:
    - documento de identidad
    - nombres y apellidos
    - fecha de nacimiento
    - sexo
    - cargo o puesto laboral
    - área o unidad organizacional
    - estado del trabajador dentro de la empresa.
- **Ejemplo de estados:**
  - activo
  - inactivo (ejemplo salio de vacaciones)
  - retirado.
- **Relación con pacientes**
  - Cuando un trabajador se registra en el sistema, puede:
    - vincularse con un paciente existente
    - generar automáticamente un nuevo registro de paciente.
  - Esto permite mantener una única identidad clínica del individuo dentro del sistema.

- **Proyecto o centro de costo**
  - Las empresas podrán organizar trabajadores por proyectos, obras o centros de costo.
  - Ejemplo:
    - Empresa: Constructora Andes
    - Proyectos:
      - Proyecto Puente Norte
      - Proyecto Mina Azul
      - Proyecto Carretera Sur
  - Esto permitirá generar reportes corporativos filtrados por proyecto o unidad operativa.

## 5. Protocolos de Evaluación Ocupacional
- **Descripción**
  - Las empresas no contratan servicios médicos individuales, sino protocolos de evaluación.
- **Definición de protocolo**
  - Un protocolo representa un conjunto de servicios médicos definidos según el tipo de evaluación requerida.
  - Un protocolo está compuesto por uno o varios servicios del catálogo médico.
  - Ejemplo:
    - Protocolo: Evaluación de ingreso minero
    - Servicios incluidos:
      - consulta médica ocupacional
      - rayos X de tórax
      - audiometría
    - evaluación psicológica.
- **Asociación de protocolo a trabajadores**
  - La empresa puede asignar protocolos a trabajadores según:
    - el puesto laboral
    - el nivel de riesgo ocupacional
    - el tipo de evaluación requerida.
  - Ejemplo
    - Operador de maquinaria pesada
    - Protocolo asignado: Evaluación ocupacional de alto riesgo.

## 6. Carga Masiva de Trabajadores
- **Descripción**
  - El sistema debe permitir a los usuarios autorizados de la empresa importar listas de trabajadores mediante archivos.
  - Esto facilita la gestión de evaluaciones médicas corporativas a gran escala.
- **Importación mediante archivo**
  - El sistema debe permitir cargar archivos en formato:
    - Excel
    - CSV.
  - El archivo puede incluir campos como:
    - DNI
    - nombres
    - cargo
    - área
    - protocolo asignado.
  - El sistema debe validar:
    - duplicados
    - formato de documento
    - consistencia de datos.

## 7. Agendamiento Corporativo
- **Descripción**
  - El sistema debe permitir que las empresas reserven espacios de atención para grupos de trabajadores.
  - Este mecanismo facilita la gestión de evaluaciones médicas masivas.
- **Reserva de bloques de citas**
  - Cuando se reserva un bloque corporativo, el sistema debe bloquear esos espacios en la agenda médica para evitar que sean utilizados por citas individuales.
  - Ejemplo:
    - Empresa: Constructora Andes
    - Fecha: lunes 15
    - Horario: 8:00 – 12:00
    - Cantidad de cupos: 20 trabajadores.
  - Posteriormente, estos cupos pueden ser asignados a trabajadores específicos.
- **Liberación automática de cupos**
  - El sistema debe permitir configurar una regla de liberación automática de cupos.
  - Ejemplo:
    - Si 24 horas antes de la cita existen cupos corporativos sin trabajadores asignados, estos podrán liberarse automáticamente para agendamiento individual.

## 8. Dashboard Corporativo
- **Descripción**
  - El sistema debe proporcionar a las empresas métricas sobre el estado de las evaluaciones médicas de sus trabajadores.
  - Estas métricas deben respetar las normas de confidencialidad médica.
- **Estado operativo**
  - Ejemplos de indicadores:
    - trabajadores evaluados
    - trabajadores pendientes
    - citas programadas
    - ausencias a citas.
- **Métricas de salud agregadas**
  - El sistema puede mostrar métricas estadísticas sin revelar información clínica individual.
  - Ejemplos:
    - prevalencia de estrés laboral
    - incidencias de problemas auditivos
    - indicadores de riesgo ocupacional.

## 9. Gestión Documental Corporativa
- **Descripción**
  - El sistema debe permitir generar y almacenar documentos asociados a las evaluaciones médicas ocupacionales.
- **Documentos disponibles para la empresa**
  - Ejemplos:
    - certificado de aptitud laboral
    - constancias de evaluación médica
    - reportes de cumplimiento de evaluaciones.
  - Estos documentos podrán ser descargados por los usuarios autorizados de la empresa.

## 10. Privacidad y Acceso a Información Clínica
- **Descripción**
  - El sistema debe garantizar la confidencialidad de la información médica individual de los trabajadores.
  - Los usuarios de la empresa no pueden acceder a la historia clínica ni a las notas médicas detalladas.
  - Solo podrán visualizar:
    - estado de aptitud laboral
    - certificados ocupacionales
    - reportes agregados de salud.
  - Esto permite cumplir con las normativas de protección de datos y legislación laboral.
- **Estados de aptitud ocupacional**
  - El sistema debe permitir registrar los siguientes estados de aptitud laboral:
    - Apto
    - Apto con restricciones
    - No apto
    - Observado o pendiente
  - Cuando el estado sea Apto con restricciones, el sistema debe permitir registrar restricciones laborales.
  - Ejemplos de restricciones:
    - no levantar peso mayor a 10 kg
    - evitar exposición prolongada a ruido
    - evitar trabajo nocturno
  - Las empresas podrán visualizar las restricciones laborales, pero no el diagnóstico médico asociado.
- **Consentimiento para compartir resultados ocupacionales**
  - Durante el proceso de evaluación ocupacional, el sistema debe registrar el consentimiento del trabajador para compartir con su empleador el resultado de su evaluación de aptitud laboral.
  - Este consentimiento permite que la empresa pueda visualizar en el Portal B2B:
    - estado de aptitud laboral
    - restricciones laborales aplicables
    - certificados ocupacionales.
  - El consentimiento no autoriza el acceso a la historia clínica ni a los diagnósticos médicos del trabajador.
  - El sistema debe permitir registrar:
    - fecha de aceptación del consentimiento
    - identificación del trabajador
    - versión del documento de consentimiento firmado.
  - Opcionalmente, el sistema puede almacenar:
    - documento firmado digitalmente
    - registro de aceptación electrónica.

## 11. Portal de Empresa (Portal B2B)
- **Descripción**
  - Las empresas deben interactuar con el sistema mediante un portal independiente del sistema interno de la clínica.
  - Este portal permitirá que los clientes corporativos puedan:
    - gestionar trabajadores
    - asignar protocolos
    - agendar evaluaciones
    - consultar reportes
    - descargar documentos.
  - El portal B2B operará como una interfaz externa conectada al sistema clínico mediante APIs.

## 📌 Nota de Arquitectura
- El módulo B2B se integra con los siguientes componentes del sistema:
  - Catálogo de Servicios → para construir protocolos médicos
  - Pacientes → para gestionar identidad clínica de trabajadores
  - Agenda médica → para reservar espacios de evaluación
  - Facturación → para gestionar cobros corporativos.