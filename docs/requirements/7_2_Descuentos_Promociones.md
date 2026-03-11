# 📋 Requerimiento Funcional: Gestión de Descuentos y Promociones
## 1. Descripción del módulo
- El módulo de Descuentos y Promociones permite administrar beneficios comerciales que la clínica ofrece directamente a los pacientes, con el objetivo de incentivar el uso de servicios médicos o apoyar campañas institucionales.
- A diferencia de los seguros o convenios institucionales, estos descuentos:
  - no dependen de una aseguradora
  - no dependen de una institución externa
- Son definidos internamente por la clínica
- El objetivo del módulo es permitir aplicar reducciones temporales o permanentes en el precio de los servicios, según reglas definidas por la clínica.

## 2. Gestión de Descuentos
- El sistema debe permitir crear y administrar descuentos aplicables a los servicios de la clínica.
- Información del descuento:
  - nombre del descuento
  - tipo de descuento (porcentaje o monto fijo)
  - valor del descuento
  - descripción o motivo del descuento
  - estado (activo / inactivo)
- Ejemplos:
  - Descuento Adulto Mayor
  - Campaña Preventiva de Salud
  - Descuento Cumpleaños
  - Promoción Chequeo Anual

## 3. Configuración del Alcance del Descuento
- El sistema debe permitir definir a qué se aplica el descuento.
- Puede aplicarse a:
  - todos los servicios
  - servicios específicos
  - especialidades médicas
  - protocolos médicos completos.
- Ejemplo:
  - Descuento: 10%
  - Aplica a: laboratorio clínico

## 4. Configuración de Vigencia
- Los descuentos pueden ser temporales o permanentes.
- El sistema debe permitir configurar:
  - fecha de inicio
  - fecha de fin
  - estado del descuento.
- Ejemplo:
  - Campaña de verano
  - Inicio: 01 enero
  - Fin: 31 marzo

## 5. Segmentación de Pacientes
- El sistema debe permitir aplicar descuentos solo a determinados grupos de pacientes.
- Ejemplos:
  - adultos mayores
  - niños
  - pacientes recurrentes
  - primera consulta
  - trabajadores de la clínica.
- **Información de segmentación**
  - Puede incluir:
    - edad mínima o máxima
    - número de visitas previas
    - tipo de paciente.

## 6. Aplicación por Sede
- Si la clínica tiene varias sedes, el sistema debe permitir definir si el descuento aplica:
  - a todas las sedes
  - solo a sedes específicas.
- Esto permite ejecutar campañas promocionales locales.
- Ejemplo:
  - Promoción laboratorio
  - Solo sede Lima Norte

## 7. Reglas de Aplicación del Descuento
- **Prioridad del beneficio**
    - El sistema debe permitir definir la prioridad del descuento frente a otros beneficios del sistema.
- **Información adicional**
    - prioridad frente a seguros
    - prioridad frente a convenios
    - posibilidad de combinación
- **Exclusividad del descuento**
    - El sistema debe permitir indicar si el descuento es exclusivo.
    - Si el descuento es exclusivo:
        - no puede combinarse con seguros
        - no puede combinarse con convenios
        - no puede combinarse con otros descuentos
    - Ejemplo:
        - Promoción Chequeo Preventivo
        - Exclusivo: Sí
    - Resultado:
        - No se aplican seguros ni convenios
        - solo la promoción
- Si el descuento no es exclusivo, el sistema puede combinar beneficios.

## 8. Validación Automática
- Cuando se registra una cita o servicio, el sistema debe validar automáticamente:
  - si existe algún descuento activo
  - si el paciente cumple las condiciones
  - si el servicio aplica al descuento.
- Si se cumplen las condiciones, el sistema debe calcular el precio final.

## 9. Cálculo del Descuento
- El sistema debe calcular automáticamente el monto del descuento.
- Ejemplo:
  - Precio servicio: 120
  - Descuento: 10%
  - Precio final: 108
  o
  - Precio servicio: 120
  - Descuento fijo: 20
  - Precio final: 100

## 10. Historial de Aplicación de Descuentos
- El sistema debe registrar cuándo se aplicó un descuento en una atención.
- El historial debe incluir:
  - paciente
  - servicio realizado
  - descuento aplicado
  - precio original
  - precio final
  - fecha de atención

## 11. Códigos Promocionales
- El sistema debe permitir definir códigos promocionales asociados a campañas de descuento.
- **Información del código:**
  - código promocional
  - descuento asociado
  - fecha de vigencia
  - número máximo de usos
  - estado del código
- **Ejemplo:**
  - Código: SALUD2026
  - Descuento: 15%
  - Vigencia: 01/06/2026 - 30/06/2026
- **Aplicación:**
  - El descuento solo se aplica si el paciente proporciona el código al momento del registro de la cita o atención.

## Relación con otros módulos
- Este módulo se conecta con:
  - Pacientes → para validar segmentación
  - Catálogo de Servicios → para aplicar descuentos a servicios
  - Protocolos Médicos → para aplicar descuentos a paquetes de exámenes
  - Agenda Médica → para calcular el precio al agendar
  - Facturación → para registrar el precio final pagado