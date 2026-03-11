# 📋 Requerimiento Funcional: Gestión de Convenios Institucionales
## 1. Descripción del módulo
- El módulo de Convenios Institucionales permite administrar acuerdos comerciales entre la clínica y distintas organizaciones, mediante los cuales se ofrecen precios preferenciales para determinados servicios médicos.
- Estos convenios pueden establecer condiciones especiales para:
  - empresas
  - universidades
  - instituciones públicas
  - asociaciones u organizaciones privadas
- El objetivo del módulo es permitir que el sistema aplique automáticamente tarifas preferenciales o condiciones especiales cuando un paciente pertenece a una institución con convenio vigente.

## 2. Gestión de Instituciones con Convenio
- El sistema debe permitir registrar las instituciones con las cuales la clínica mantiene convenios.
- Estas instituciones pueden ser:
  - empresas
  - universidades
  - institutos
  - asociaciones
  - entidades públicas
- Información de la institución:
  - nombre de la institución
  - tipo de institución (empresa, universidad, asociación, etc.)
  - código interno
  - número de identificación (RUC si aplica)
  - dirección
  - datos de contacto
  - estado del convenio (activo / inactivo)

## 3. Gestión de Convenios
- Una institución puede tener uno o varios convenios con la clínica.
- Cada convenio define las condiciones comerciales aplicables.
- Información del convenio:
  - institución asociada
  - nombre del convenio
  - fecha de inicio
  - fecha de fin
  - estado (activo / inactivo)
  - descripción o condiciones generales
- Esto permite manejar convenios temporales o renovables.

## 4. Configuración de Tarifas Preferenciales
- El sistema debe permitir definir precios especiales asociados a cada convenio.
- Estas tarifas pueden configurarse para:
  - servicios individuales
  - protocolos médicos completos.
- Ejemplo:
  - Precio normal:
    - Consulta médica: S/120
  - Precio con convenio:
    - Consulta médica: S/90
- El sistema debe utilizar este precio cuando el paciente pertenece a la institución con convenio activo.

## 5. Descuentos por Porcentaje
- Además de precios fijos, el sistema debe permitir aplicar descuentos porcentuales.
- Ejemplo:
  - Descuento convenio: 15%
  - Precio servicio:
    - 120 - 15% = 102

## 6. Asociación del Paciente a una Institución
- El sistema debe permitir registrar que un paciente pertenece a una institución con convenio.
- **Información requerida:**
  - paciente
  - institución
  - tipo de relación (trabajador, estudiante, miembro)
  - número de identificación institucional (si aplica)
  - fecha de registro
  - estado (activo / inactivo)
- Esto permitirá aplicar automáticamente el convenio al momento de registrar una cita o atención.
- **Documento de validación (opcional)**
- El sistema debe permitir registrar o adjuntar un documento que
  acredite la pertenencia del paciente a la institución con convenio.
- Ejemplos:
  - fotocheck laboral
  - carnet universitario
  - credencial institucional

## 7. Validación del Convenio
- Cuando se registra una cita o servicio, el sistema debe validar:
  - si el paciente pertenece a una institución con convenio
  - si el convenio está vigente
  - si el servicio o protocolo tiene tarifa preferencial
- Si se cumplen las condiciones, el sistema aplicará automáticamente el precio correspondiente.

## 8. Reglas de Aplicación del Convenio
- El sistema debe permitir configurar reglas sobre cómo se aplica el convenio.
- Por ejemplo:
  - si el convenio aplica a todos los servicios
  - si aplica solo a ciertos servicios
  - si aplica solo a ciertos protocolos médicos
- También debe permitir definir si el convenio puede combinarse con otros descuentos o beneficios.
- **Prioridad de aplicación**
- El sistema debe permitir definir la prioridad del convenio frente
  a otros beneficios disponibles, como seguros o descuentos.
- Ejemplo de jerarquía:
  - Seguros / EPS
  - Convenios institucionales
  - Descuentos promocionales
- El sistema debe aplicar automáticamente el beneficio según
  la prioridad configurada.

## 9. Historial de Uso del Convenio
- El sistema debe registrar cuándo un servicio fue atendido bajo un convenio.
- El historial debe incluir:
  - paciente
  - institución asociada
  - servicio realizado
  - precio normal del servicio
  - precio aplicado por convenio
  - fecha de atención
- Esto permitirá generar reportes de uso del convenio.

## 10. Aplicación del Convenio por Sede
- El sistema debe permitir definir si un convenio aplica:
  - a todas las sedes de la clínica
  - solo a sedes específicas.
- Esto permitirá que los precios preferenciales se apliquen
  únicamente en las ubicaciones autorizadas.
- Ejemplo:
  - Convenio: Empresa Minera XYZ
  - Sede habilitada: Clínica Huaraz

## 📊 Relación con otros módulos
- Este módulo se conecta con:
  - Pacientes → para identificar la institución del paciente
  - Catálogo de Servicios → para definir tarifas preferenciales
  - Protocolos Médicos → para aplicar tarifas a evaluaciones ocupacionales
  - Agenda Médica → para calcular el precio al agendar
  - Facturación → para registrar el monto pagado bajo convenio