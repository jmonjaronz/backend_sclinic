# 📋 Requerimiento Funcional: Gestión de Seguros / EPS

## 1. Descripción del módulo
- El módulo de Seguros / EPS permite administrar las aseguradoras con las que la clínica tiene convenio, así como las condiciones de cobertura que estas ofrecen para los servicios médicos.
- Este módulo permite que el sistema determine:
  - qué servicios están cubiertos por cada seguro
  - cuánto paga el seguro
  - cuánto paga el paciente (copago o coaseguro)
- Su objetivo es calcular correctamente la responsabilidad de pago entre paciente y aseguradora.

## 2. Gestión de Aseguradoras
- El sistema debe permitir registrar las aseguradoras con las que la clínica trabaja.
- **Información de la aseguradora**
  - Debe incluir:
    - nombre de la aseguradora
    - tipo de aseguradora (EPS o seguro privado)
    - código interno
    - estado (activo / inactivo)
    - datos de contacto administrativos
  - Ejemplos:
    - Pacífico
    - Rímac
    - Mapfre
    - La Positiva

## 3. Gestión de Planes de Seguro
- Cada aseguradora puede tener varios planes con diferentes niveles de cobertura.
- Ejemplo:
  - Pacífico puede tener:
    - Plan Básico
    - Plan Plus
    - Plan Corporativo
- El sistema debe permitir registrar los planes asociados a cada aseguradora.
- Información del plan
  - aseguradora asociada
  - nombre del plan
  - tipo de red médica (cerrada / abierta)
  - requiere autorización previa (sí / no)
  - estado (activo / inactivo)

## 4. Cobertura de Servicios
- El sistema debe permitir definir qué servicios cubre cada plan de seguro.
- Esto se vincula directamente con el Catálogo de Servicios.
- Para cada servicio se deben definir las condiciones de cobertura.

## 5. Configuración de Copago
- El copago es el monto fijo que paga el paciente por un servicio.
- Ejemplo:
  - Consulta médica:
    - Precio servicio: S/120
    - Copago: S/40
  - Paciente paga: S/40
  - Seguro paga: S/80
- El sistema debe permitir configurar copagos por:
  - servicio
  - especialidad
  - protocolo.

## 6. Configuración de Coaseguro
- El coaseguro es el porcentaje del servicio que paga el paciente.
- Ejemplo:
  - Precio consulta: S/120
  - Cobertura del seguro: 80%
  - Paciente paga: S/24
  - Seguro paga: S/96
- El sistema debe permitir definir el porcentaje de coaseguro.

## 7. Reglas de Cobertura
- El sistema debe permitir definir reglas de cobertura como:
  - servicios cubiertos
  - servicios no cubiertos
  - límites de cobertura
  - cantidad máxima de atenciones.
- Ejemplo:
  - Un seguro puede cubrir:
    - 2 consultas por mes
    - Después de eso el paciente paga el precio completo.

## 8. Asociación del Seguro al Paciente
- El sistema debe permitir registrar el seguro del paciente.
- Información requerida:
  - paciente
  - aseguradora
  - plan
  - titular o dependiente
  - nombre del titular (si es dependiente)
  - número de póliza
  - fecha de afiliación
  - fecha de vigencia
  - estado del seguro
- Esto permitirá que el sistema aplique automáticamente el beneficio al momento de registrar una cita o atención.

## 9. Validación de Cobertura
- Cuando se registra una cita o servicio, el sistema debe validar automáticamente:
  - si el paciente tiene seguro activo
  - si el servicio está cubierto
  - cuál es el copago o coaseguro.
- **Registro de autorización**
  - Para los seguros que lo requieran, el sistema debe permitir registrar
    un código de autorización emitido por la aseguradora (ejemplo: SITEDS).
  - Este código se asocia a la atención o cita y es necesario para
    la posterior facturación a la aseguradora.

## 10. Cálculo de Pago
- El sistema debe calcular automáticamente el monto que corresponde
  pagar al paciente y a la aseguradora según la configuración
  de copago o coaseguro del plan.
- Ejemplo:
  - Precio servicio: 120
  - Cobertura seguro: 80%
  - Paciente paga: 24
  - Seguro paga: 96
## 11. Registro de Cuenta por Cobrar a la Aseguradora
- El sistema debe registrar el monto que debe pagar la aseguradora para efectos de facturación.
- Esto permitirá generar reportes de:
  - cuentas por cobrar a aseguradoras
  - liquidación de servicios cubiertos.

## 12. Historial de Uso del Seguro
- El sistema debe registrar el historial de servicios utilizados
  por el paciente bajo su seguro, incluyendo:
  - servicio realizado
  - fecha de atención
  - monto cubierto por el seguro
  - monto pagado por el paciente
  - código de autorización (si aplica)

## 📊 Relación con otros módulos
- Este módulo se conecta con:
  - Pacientes → para conocer el seguro del paciente
  - Catálogo de Servicios → para definir qué servicios cubre el seguro
  - Agenda Médica → para calcular el copago al agendar
  - Facturación → para registrar la cuenta a la aseguradora.