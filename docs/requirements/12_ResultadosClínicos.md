# 📑 Módulo: Gestión de Resultados Clínicos
- **Descripción General**
    - El módulo de Gestión de Resultados Clínicos permite administrar todo el ciclo de vida de los exámenes médicos solicitados durante la consulta.
    - Este módulo conecta diferentes áreas de la clínica, tales como:
        - laboratorio
        - radiología
        - diagnóstico ocupacional
        - cardiología
        - otras áreas de diagnóstico
    - Su objetivo es garantizar que:
        - las órdenes médicas lleguen correctamente al área correspondiente
        - los resultados se registren en el sistema
        - el médico pueda revisarlos dentro de la historia clínica
        - se identifiquen valores críticos de forma inmediata

## 1. Generación de órdenes médicas
- Cuando el médico solicita un examen desde la Historia Clínica Electrónica, el sistema debe generar una orden clínica.
- Ejemplos de órdenes:
    - Hemograma completo
    - Perfil lipídico
    - Radiografía de tórax
    - Ecografía abdominal
    - Audiometría ocupacional
    - Espirometría
- Cada orden debe contener:
    - paciente
    - médico solicitante
    - fecha y hora
    - tipo de examen
    - prioridad (normal / urgente)
    - observaciones clínicas

## 2. Registro de órdenes en el área correspondiente
- Una vez generada la orden, el sistema debe enviarla automáticamente al área responsable.
- Ejemplo de flujo:
    - Médico solicita laboratorio
    - Orden aparece en bandeja del laboratorio
    - Laboratorio registra toma de muestra
    - Laboratorio procesa examen
    - Resultado se registra en el sistema
- Esto evita el uso de órdenes en papel.

## 3. Registro de resultados
- Cada área diagnóstica debe poder registrar los resultados de los exámenes.
- Los resultados pueden incluir:
    - Datos estructurados
    - Ejemplo:
        - Glucosa: 98 mg/dL
        - Hemoglobina: 13.2 g/dL
        - Colesterol: 210 mg/dL
    - Informes clínicos
    - Algunos exámenes requieren interpretación médica.
    - Ejemplo:
        - Radiografía de tórax: No se evidencian lesiones pulmonares activas.
    - Archivos adjuntos
- El sistema debe permitir adjuntar:
    - imágenes médicas
    - documentos PDF
    - informes escaneados

## 4. Validación de resultados
- En algunos casos, los resultados deben ser validados por un profesional responsable antes de liberarse.
- Ejemplo:
    - Bioquímico valida resultado de laboratorio
    - Radiólogo firma informe de radiografía
- El sistema debe registrar:
    - profesional que validó
    - fecha y hora de validación

## 5. Valores críticos
- El sistema debe identificar automáticamente resultados críticos.
- Ejemplo:
    - Hemoglobina: 6.5 g/dL
    - Glucosa: 450 mg/dL
    - Potasio: 6.8 mmol/L
- Cuando ocurre esto, el sistema debe:
    - marcar el resultado como crítico
    - resaltar el valor en la interfaz
    - notificar al médico tratante
- Ejemplo visual:
    - Glucosa: 450 mg/dL   ⚠ VALOR CRÍTICO
## 6. Notificación al médico
- Cuando un resultado esté disponible, el sistema debe notificar al médico solicitante.
- Opciones de notificación:
    - alerta en el sistema
    - bandeja de resultados pendientes
    - notificación interna
- Esto permite que el médico revise resultados incluso después de finalizada la consulta.

## 7. Integración con la Historia Clínica
- Los resultados deben integrarse automáticamente con la historia clínica del paciente.
- El médico debe poder ver:
    - resultados actuales
    - resultados anteriores
    - evolución de valores clínicos
- Ejemplo:
    - Glucosa
        - 2024: 110
        - 2025: 135
        - 2026: 180
- Esto permite visualizar tendencias clínicas.

## 8. Resultados para el paciente
- El sistema debe permitir que los resultados estén disponibles para el paciente.
- Opciones posibles:
    - portal del paciente
    - descarga de informes
    - impresión de resultados
- Esto reduce la necesidad de acudir físicamente a recoger informes.