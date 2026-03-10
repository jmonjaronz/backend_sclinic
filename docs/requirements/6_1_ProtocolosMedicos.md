# 📦 Requerimiento Funcional: Gestión de Protocolos Médicos
El módulo de Protocolos Médicos permite definir conjuntos de servicios clínicos que son utilizados para evaluaciones médicas ocupacionales o corporativas.
- Un protocolo representa un paquete estructurado de servicios médicos, diseñado para evaluar a un trabajador según su puesto laboral o nivel de riesgo.
- Este módulo actúa como un puente entre:
    - el Catálogo de Servicios
    - el Módulo de Empresas (B2B)
    - el sistema de Agenda Médica
- Los protocolos permiten simplificar la gestión de evaluaciones médicas corporativas y garantizar que cada trabajador reciba los exámenes correspondientes a su perfil laboral.

## 1. Definición de Protocolo
- **Descripción**
  - El sistema debe permitir crear y administrar protocolos médicos utilizados para evaluaciones ocupacionales o corporativas.
  - Un protocolo agrupa múltiples servicios del catálogo bajo una estructura lógica que representa un tipo de evaluación.
  - Ejemplo:
    - Protocolo: Evaluación de ingreso para trabajo en altura
    - Servicios incluidos:
      - consulta médica ocupacional
      - audiometría
      - espirometría
      - evaluación psicológica
      - examen de visión.
- **Información del protocolo**
  - El sistema debe permitir registrar la siguiente información:
    - nombre del protocolo
    - descripción
    - tipo de evaluación (ingreso, periódico, retiro u otros)
    - estado del protocolo (activo / inactivo).
- **Cuando un protocolo se encuentre inactivo:**
  - no podrá asignarse a nuevos trabajadores
  - pero su historial debe conservarse.

## 2. Servicios asociados al protocolo
- **Descripción**
  - Cada protocolo debe permitir asociar uno o más servicios provenientes del Catálogo de Servicios Médicos.
  - Esto permite construir evaluaciones médicas completas a partir de servicios individuales.
- **Configuración de servicios**
  - Para cada servicio dentro del protocolo el sistema debe permitir definir:
    - orden de ejecución del examen
    - obligatoriedad del servicio
    - duración estimada del servicio.
    - Ejemplo:
      - Protocolo: Evaluación Minera
      - Orden	Servicio
      - 1	Consulta médica
      - 2	Rayos X
      - 3	Audiometría
      - 4	Psicología
- Este orden puede ser utilizado posteriormente por el sistema de agenda médica para optimizar la secuencia de atención.

## 3. Precios por protocolo
- **Descripción**
  - El sistema debe permitir definir precios de protocolo diferenciados para cada empresa cliente.
  - Esto permite que la clínica ofrezca condiciones comerciales específicas según el contrato corporativo.
- **Configuración de precios**
  - El sistema debe permitir registrar:
    - precio base del protocolo
    - precio por empresa o convenio
    - vigencia del precio.
    - Ejemplo:
      - Protocolo: Evaluación Minera
      - Precio general: 250
      - Empresa A: 220
      - Empresa B: 200.
    - Esto permite mantener un único protocolo clínico con múltiples configuraciones comerciales.

## 4. Protocolos según perfil de riesgo
- **Descripción**
  - El sistema debe permitir asociar protocolos a perfiles de riesgo laboral o tipos de puesto.
  - Esto permite automatizar la asignación de evaluaciones médicas según la actividad del trabajador.
- **Ejemplo de configuración**
  - Puesto laboral: Chofer
  - Protocolo asignado:
    - examen de visión
    - evaluación psicológica
    - consulta médica ocupacional.
  - Puesto laboral: Operador de maquinaria pesada
  - Protocolo asignado:
    - audiometría
    - examen de visión
    - evaluación médica ocupacional
    - evaluación psicológica.
- **Automatización**
  - Cuando se registre un trabajador y se seleccione su puesto laboral, el sistema podrá sugerir automáticamente el protocolo correspondiente.
  - Esto reduce errores en la asignación de evaluaciones médicas.

## 5. Versionado de protocolos
- **Descripción**
  - Los protocolos médicos pueden cambiar con el tiempo debido a:
    - cambios normativos
    - ajustes médicos
    - requerimientos de empresas.
  - Por ello, el sistema debe permitir mantener versiones de protocolos.
- **Ejemplo**
  - Protocolo: Evaluación Minera
  - Versión 1 (2024):
    - consulta médica
    - audiometría
    - rayos X.
  - Versión 2 (2025):
    - consulta médica
    - audiometría
    - rayos X
    - espirometría.
  - Las evaluaciones realizadas deben quedar asociadas a la versión del protocolo vigente en el momento de la evaluación.

## 6. Relación con Agenda Médica
- **Descripción**
  - Los protocolos médicos se utilizarán como base para generar las citas médicas de los trabajadores.
  - Cuando un trabajador sea asignado a un protocolo, el sistema podrá generar automáticamente las citas necesarias para completar todos los servicios incluidos.
- **Ejemplo**
  - Protocolo:
    - consulta médica
    - audiometría
    - psicología.
  - El sistema deberá generar tres citas o etapas de atención dentro de la agenda médica.

## 7. Integración con el módulo B2B
- **Descripción**
  - Los protocolos serán utilizados por las empresas para solicitar evaluaciones médicas para sus trabajadores.
  - Las empresas podrán:
    - seleccionar protocolos disponibles
    - asignarlos a trabajadores
    - programar evaluaciones médicas basadas en dichos protocolos.
  - Esto permite estandarizar las evaluaciones ocupacionales solicitadas por cada organización.