# 🏗️ Requerimiento Técnico: Infraestructura Saas, Multi-Tenancy y Aislamiento de Datos 
Este módulo establece los cimientos arquitectónicos del sistema SaaS
Su propósito es garantizar:
- **Aislamiento total entre clínicas (multi-tenant seguro):** Este componente es el "muro de seguridad" del sistema. Su objetivo es garantizar que ninguna clínica pueda acceder a datos de otra, incluso por error humano en el desarrollo.
- **Capacidad de personalización por cliente (white-label):** Cada clínica puede adaptar la apariencia del sistema.
- **Escalabilidad del producto:** La arquitectura debe soportar múltiples clínicas sin duplicar infraestructura.
- **Control comercial mediante módulos y cuotas:** El acceso a funcionalidades depende del plan contratado.

## 1. Componente: ClinicGlobalManager (Aislamiento a nivel de Modelo)
- **Descripción:** 
    - El aislamiento de datos entre clínicas debe implementarse a nivel del modelo de datos, no únicamente en las vistas o endpoints.
    - Para ello se utilizará un Manager personalizado de Django, encargado de aplicar automáticamente el filtro de clínica en todas las consultas.
- **Funcionamiento:**
    - Toda consulta realizada mediante el manager principal del modelo incluirá automáticamente el filtro correspondiente a la clínica actual.
    - De esta forma, el sistema garantiza que:
        - las consultas solo devuelvan datos de la clínica activa
        - el aislamiento no dependa del programador que implementa la vista
        - los errores humanos no comprometan la seguridad de los datos
- **Consultas Globales:**
    - Para operaciones administrativas del sistema (SuperAdmin), se definirá un método explícito que permita acceder a los datos globales sin aplicar el filtro automático.
    - Este acceso estará restringido únicamente a contextos administrativos del sistema.
- **Beneficio:** 
    - Este enfoque garantiza seguridad por defecto.
    - Incluso si un desarrollador olvida aplicar filtros manuales, el sistema continuará protegiendo los datos de cada clínica.

## 2. Componente: MultiDomainMiddleware (Identificación Dinámica de Clínicas)
- **Descripción:** 
    - Este componente es responsable de identificar qué clínica está realizando la solicitud al sistema.
    - Funciona como un motor de detección de inquilino (tenant) basado en el dominio o subdominio desde el cual se accede al sistema.
- **Funcionamiento:**
    - El middleware analiza el host del request HTTP y lo compara con los dominios registrados en el sistema para determinar a qué clínica pertenece la solicitud.
    - Una vez identificada la clínica:
        - se carga su configuración
        - se asocia al contexto de la petición
- **Independencia de Dominio**
    - El sistema no depende de un dominio fijo.
    - Esto permite soportar distintos escenarios como:
        - subdominios del sistema principal
        - dominios personalizados de cada clínica
        - implementaciones white-label
    - Cada dominio estará asociado internamente a una clínica específica.
- **Inyección de Contexto**
    - Después de identificar la clínica, el middleware adjunta el objeto de la clínica al contexto del request.
    - Esto permite que cualquier componente del sistema pueda acceder a la clínica actual sin realizar consultas adicionales a la base de datos.

# 🔐 Requerimiento de Seguridad: ClinicIsolationMixin para la API
- **Nombre del Requerimiento:** 
    - Mixin de Aislamiento de Queryset.
- **Descripción:** 
    - Clase base de seguridad que deberá ser heredada por todos los ViewSets de la API.
    - Su objetivo es garantizar que todas las consultas realizadas desde la API estén restringidas a la clínica correspondiente al usuario autenticado.
- **Lógica del Componente:**
    - El mixin implementa tres validaciones principales:
    - **Validación de sesión:** 
        - Verifica que el usuario autenticado pertenezca a la clínica identificada en el contexto del request.
    - **Restricción automática de consultas:** 
        - Sobrescribe el método encargado de obtener los datos para asegurar que los resultados estén siempre limitados a la clínica actual.
        - Esto garantiza que los parámetros enviados por el usuario no puedan modificar el alcance de los datos.
    - **Falla segura:** 
        - Si el sistema no puede identificar una clínica válida en la solicitud, la API no devolverá información.
        - En ese caso se responderá con un error de acceso o con un conjunto de datos vacío.
        - Esto asegura que nunca se expongan datos globales por error.

# 🎨 Requerimiento Funcional: Whitelabel y Configuración Modular
Este módulo permite que el sistema pueda adaptarse visual y funcionalmente a cada cliente, permitiendo que la plataforma se utilice como si fuera un software desarrollado específicamente para cada clínica.

## 1. Funcionalidad: DynamicBrandingEngine (Motor de Marca)
-   **Descripción:**
    - Componente encargado de gestionar la identidad visual personalizada de cada clínica.
    - Este motor permite que el frontend obtenga la configuración visual correspondiente y la aplique dinámicamente.
-   **Alcance:**
    - El motor permitirá gestionar:
    - Identidad visual: logotipos, isotipos y favicon por clínica.
    - Personalización de interfaz: definición de paleta de colores que el frontend aplicará dinámicamente.
    - Nomenclatura personalizada: posibilidad de modificar etiquetas utilizadas en la interfaz según la preferencia de cada clínica.
-   **Beneficios:**
    - Este sistema permite implementar white-label sin modificar el código del frontend.

## 2. Funcionalidad: FeatureToggling (Habilitación de Módulos)
-   **Descripción:**
    - Sistema encargado de activar o desactivar funcionalidades del sistema según el contrato comercial de cada clínica.
    - Cada funcionalidad del sistema puede controlarse mediante un interruptor lógico (feature flag).
-   **Alcance:**
    - Esto permite habilitar módulos específicos sin necesidad de modificar el código ni desplegar nuevas versiones del sistema.
-   **Flags Iniciales del Sistema:**
    - El sistema deberá considerar por defecto los siguientes módulos activables:
        - `module_psychology`: habilita evaluaciones psicológicas, baremos y notas de evolución mental.
        - `module_laboratory`: habilita gestión de muestras y órdenes de laboratorio.
        - `module_occupational`: habilita funcionalidades orientadas a medicina ocupacional.
        - `module_hospitalization`: habilita gestión de hospitalización y control de camas.
        - `module_emergency`: habilita flujos de atención de emergencia y triaje.
        - `module_imaging`: habilita gestión de estudios de imágenes médicas.
        - `module_pharmacy`: habilita control de inventario farmacéutico y recetas electrónicas.
        - `module_specialties_med`: habilita historias clínicas específicas por especialidad.
        - `module_analytics_advanced`: habilita dashboards y reportes avanzados.
-   **Beneficios:**
    - El sistema debe permitir agregar nuevos flags en el futuro sin modificar la arquitectura existente.
-   **Límites de Uso (Quotas):**
    - Además de habilitar módulos, el sistema debe permitir definir límites de uso asociados al plan contratado.
    - Estos límites permiten controlar el consumo de recursos y establecer diferentes niveles de servicio.
    - Los límites iniciales a considerar son:
        - `limit_storage_files`: capacidad total de almacenamiento de archivos.
        - `limit_active_specialists`: número máximo de especialistas activos.
        - `limit_headquarters`: cantidad de sedes que la clínica puede administrar.
        - `limit_monthly_appointments`: límite mensual de citas generadas.
    - Estos límites podrán ajustarse según el plan comercial o acuerdos específicos con cada cliente.