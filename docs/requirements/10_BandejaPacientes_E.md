# 🩺 Módulo: Bandeja de Pacientes del Especialista
- **Descripción General**
    - La Bandeja de Pacientes del Especialista es el panel de control desde donde el médico gestiona la atención de los pacientes asignados a su agenda.
    - Este componente permite visualizar en tiempo real el estado de los pacientes dentro del flujo clínico y facilita iniciar, pausar o finalizar la consulta médica.
    - La bandeja debe ser simple, rápida de interpretar y orientada a la toma de decisiones.

## 1. Monitor de Atención en Tiempo Real
- El sistema debe mostrar una lista dinámica de los pacientes que han sido admitidos y están dentro del flujo de atención del especialista durante el día.
- Esta bandeja se actualiza automáticamente cuando ocurren cambios en el estado del paciente.
- Ejemplo:
    - Paciente llega
    - Recepción realiza check-in
    - Triaje (si aplica)
    - Paciente aparece en la bandeja del especialista

## 2. Información Visible en la Bandeja
- Cada paciente mostrado en la bandeja debe presentar información clara y rápida de interpretar.
- Datos de identificación:
    - Nombre del paciente
    - Edad
    - Sexo
- Estado del flujo:
    - Indica en qué etapa del proceso se encuentra el paciente.
    - Ejemplo:
        - En triaje
        - Listo para atención
        - En espera
        - En consulta
- Hora de cita y tiempo de espera:
    - La bandeja debe mostrar:
        - hora de cita programada
        - tiempo de espera actual
    - El tiempo de espera debe actualizarse automáticamente mediante un contador.
    - Ejemplo:
        - Hora cita: 09:30
        - Esperando: 12 min
    - Esto permite al médico identificar retrasos o priorizar pacientes.
- Tipo de atención:
    - La bandeja debe mostrar un indicador visual del tipo de atención.
    - Ejemplo:
        - Presencial
        - Teleconsulta
        - Evaluación ocupacional
    - Se recomienda utilizar iconos visuales para facilitar la identificación rápida.
- Alertas clínicas:
    - Si durante el triaje se detecta información crítica, el sistema debe mostrar una alerta visible.
    - Ejemplo:
        - Alergia registrada
        - Presión arterial elevada
        - Observación clínica relevante
    - Esto puede representarse mediante un indicador visual como:
        - 🚩 alerta clínica

## 3. Acciones del Especialista
- Desde la bandeja el médico puede gestionar el flujo de atención de sus pacientes.
- 3.1 Llamar Paciente:
    - Permite iniciar la consulta.
    - Al ejecutarse:
        - estado del paciente → En consulta
    - Si la clínica dispone de pantallas en sala de espera, esta acción puede generar:
        - aviso visual
        - aviso sonoro
    - Indicando al paciente que debe ingresar al consultorio.
- 3.2 Iniciar Teleconsulta:
    - Si la cita es virtual, el sistema debe permitir abrir directamente la sala de video integrada.
    - Esto permite:
        - conectar médico y paciente
        - registrar inicio de consulta virtual
- 3.3 Pausar atención:
    - El médico puede pausar temporalmente la consulta si el paciente necesita realizar una acción adicional.
    - Ejemplo:
        - realizar examen
        - dirigirse a rayos X
        - buscar documento
    - El estado puede cambiar a:
        - Consulta pausada
- 3.4 Retomar atención:
    - Permite continuar una consulta previamente pausada.
- 3.5 Finalizar atención:
    - Una vez concluida la consulta, el médico puede cerrar el proceso.
    - Esto genera el cambio de estado:
        - Atendido
    - A partir de este momento el sistema puede permitir:
        - salida del paciente
        - emisión de receta
        - generación de órdenes médicas
        - programación de próxima cita

## 4. Priorización y Filtros
- La bandeja debe permitir organizar los pacientes según distintos criterios.
- Orden cronológico:
    - Ordena la lista según la hora programada de la cita.
- Orden de llegada:
    - Ordena según el momento en que el paciente terminó el proceso previo (triaje o admisión).
- Filtro por sede:
    - En casos donde el especialista atienda de forma remota en múltiples sedes, el sistema debe permitir filtrar pacientes por sede.
    - Ejemplo:
        - Sede Centro
        - Sede Norte
        - Sede Sur

## 5. Integración con Protocolos Ocupacionales (B2B)
- Cuando el especialista participa en evaluaciones ocupacionales, la bandeja debe mostrar información adicional del protocolo.
- Estado del protocolo:
    - El sistema debe indicar qué evaluaciones ya fueron completadas.
    - Ejemplo:
        - Laboratorio → completado
        - Rayos X → completado
        - Psicología → pendiente
        - Medicina ocupacional → en proceso
- Validación de cierre de evaluación:
    - El sistema no debe permitir finalizar el proceso si existen evaluaciones obligatorias pendientes.
    - Ejemplo:
        - Resultado de laboratorio pendiente
        - Evaluación psicológica no realizada
    - Esto evita emitir un informe ocupacional incompleto.

## 6. Vista Previa Rápida del Paciente
- Para mejorar la eficiencia del especialista, la bandeja debe permitir visualizar información clínica básica sin abrir la historia completa.
- Cuando el médico coloca el cursor sobre el paciente, el sistema puede mostrar una ventana flotante con información relevante.
- Ejemplo:
    - Motivo de consulta
    - Presión arterial
    - Peso
    - Talla
    - Observaciones de triaje
- Esto permite al médico prepararse antes de iniciar la consulta.