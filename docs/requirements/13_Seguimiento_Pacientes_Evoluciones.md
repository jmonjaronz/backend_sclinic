# 📑 Módulo: Seguimiento del Paciente / Evoluciones
- **Descripción General**
    - El módulo de Seguimiento del Paciente permite registrar la evolución clínica del paciente a lo largo del tiempo después de una consulta médica inicial.
    - Este módulo permite documentar:
        - cambios en el estado del paciente
        - seguimiento de tratamientos
        - resultados de exámenes solicitados
        - nuevas observaciones clínicas
    - Las evoluciones forman parte de la Historia Clínica Electrónica y permiten mantener un registro cronológico del estado de salud del paciente.

## 1. Registro de Evoluciones Clínicas
- Una evolución médica es un registro adicional que el médico realiza para documentar cambios en la condición del paciente.
- Las evoluciones deben registrarse como entradas cronológicas dentro de la historia clínica.
- Ejemplo:
    - Fecha: 15/05/2026
    - Paciente refiere disminución del dolor abdominal.
    - Se mantiene tratamiento indicado.
    - Pendiente resultado de laboratorio.
- Cada evolución debe registrar:
    - médico responsable
    - fecha y hora
    - observaciones clínicas
    - cambios en tratamiento
- **Formato sugerido de evolución (SOAP)**
    - Para facilitar la organización del registro clínico, el sistema puede sugerir el uso del formato estándar SOAP.
    -Estructura SOAP:
        - S - Subjetivo: Lo que el paciente refiere
        - O - Objetivo: Hallazgos clínicos observados por el médico.
        - A - Apreciación: Interpretación clínica del médico.
        - P - Plan: Tratamiento o acciones a seguir.
    - El uso del formato SOAP ayuda a estandarizar la documentación médica.

## 2. Timeline Clínico del Paciente
- Las evoluciones deben mostrarse en una línea de tiempo que permita visualizar la historia médica del paciente.
- Ejemplo:
    - 2024
        - Consulta general
        - Diagnóstico: gastritis
    - 2025
        - Control médico
        - Se ajusta tratamiento
    - 2026
        - Evolución clínica
        - Paciente mejora síntomas
- La línea de tiempo debe permitir visualizar distintos tipos de eventos clínicos:
    - consultas médicas
    - evoluciones clínicas
    - resultados de laboratorio
    - diagnósticos
    - procedimientos realizados
- Esto facilita que los médicos comprendan rápidamente el historial del paciente.

## 3. Seguimiento de Tratamientos
- El sistema debe permitir registrar el seguimiento de tratamientos indicados previamente.
- Ejemplo:
    - Tratamiento inicial:
        - Omeprazol 20 mg por 30 días
    - Evolución posterior:
        - Paciente refiere mejoría.
        - Se reduce dosis a 10 mg.
- **Indicadores de respuesta al tratamiento**
    - El sistema puede mostrar indicadores visuales que ayuden a evaluar la evolución del paciente.
    - Ejemplo:
        - mejoría clínica
        - tratamiento sin cambios
        - respuesta insuficiente al tratamiento
    - Estos indicadores ayudan al médico a identificar rápidamente la evolución del paciente.

## 4. Revisión de Resultados Pendientes
- Cuando el médico solicita exámenes durante una consulta, puede registrar una evolución posteriormente para analizar los resultados.
- Ejemplo:
    - Resultado de hemograma revisado.
    - Valores dentro de rango normal.
    - Se descarta anemia.
- **Marcado de resultados revisados**
    - El sistema debe permitir que el médico marque un resultado como revisado.
    - Esto permite:
        - confirmar que el médico revisó el examen
        - cerrar el ciclo clínico del resultado
        - mejorar la seguridad del paciente

## 5. Indicaciones posteriores
- El médico puede registrar nuevas indicaciones durante el seguimiento.
- Ejemplo:
    - Continuar tratamiento por 15 días más.
    - Control en un mes.

## 6. Evoluciones multidisciplinarias
- En algunos casos, varios profesionales pueden registrar evoluciones sobre el mismo paciente.
- Ejemplo:
    - Medicina general
    - Nutrición
    - Psicología
    - Fisioterapia
- Cada profesional puede registrar sus propias observaciones dentro de la historia clínica.

## 7. Integración con la Historia Clínica
- Las evoluciones deben estar integradas dentro de la Historia Clínica Electrónica del paciente.
- Esto permite que el médico pueda consultar:
    - consulta inicial
    - evoluciones posteriores
    - resultados de exámenes
    - tratamientos realizados

## 8. Registro de auditoría
- Las evoluciones forman parte del registro clínico legal del paciente.
- Por este motivo, una vez firmada la evolución, el sistema debe bloquear su edición.
- Si el médico necesita agregar información adicional, debe hacerlo mediante:
    - una nueva evolución
    - una nota aclaratoria
- Cada evolución debe registrar:
    - profesional que creó el registro
    - fecha y hora de creación
    - firma del profesional
- Esto garantiza la integridad del registro clínico y protege legalmente a la institución.