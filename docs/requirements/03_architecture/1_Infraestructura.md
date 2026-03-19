# 🏗️ Requerimiento Técnico: Infraestructura Saas, Multi-Tenancy y Aislamiento de Datos 

## 1. Requerimiento Funcional
`Descripción`
Este módulo establece los cimientos arquitectónicos del sistema SaaS
Su propósito es garantizar:
  - **Aislamiento total entre clínicas (multi-tenant seguro):** Este componente es el "muro de seguridad" del sistema. Su objetivo es garantizar que ninguna clínica pueda acceder a datos de otra, incluso por error humano en el desarrollo.
  - **Escalabilidad del producto:** La arquitectura debe soportar múltiples clínicas sin duplicar infraestructura.
  - **Capacidad de personalización por cliente (white-label):** Cada clínica puede adaptar la apariencia del sistema.
  - **Control de acceso a funcionalidades mediante módulos:** El acceso a funcionalidades depende del plan contratado.
  - **Control de consumo mediante límites (quotas):** El consumo de recursos está limitado según el plan contratado.

`Objetivos`
  - Garantizar que ninguna clínica acceda a datos de otra
  - Permitir que múltiples clínicas usen el sistema en una misma infraestructura
  - Adaptar visual y funcionalmente el sistema por cliente
  - Controlar el acceso a funcionalidades según contrato
  - Preparar el sistema para crecimiento horizontal

## 2. Reglas de Negocio (Lógica SaaS)
### 2.1 Aislamiento de datos
  - Toda entidad del sistema debe pertenecer a una clínica
  - Ninguna operación puede ejecutarse sin contexto de clínica
  - Si no se puede determinar la clínica:
    - el sistema debe fallar de forma segura (no devolver datos)
### 2.2 Acceso a funcionalidades (Features)
  - Cada clínica tiene un conjunto de módulos habilitados
  - El acceso a funcionalidades:
    - debe validarse SIEMPRE en backend
    - Nota: El frontend no es considerado seguro
Ejemplo:
  - Clínica A:
    - module_laboratory → habilitado
  - Clínica B:
    - module_laboratory → deshabilitado
  - Resultado:
    - Clínica B no puede acceder a endpoints de laboratorio
### 2.3 Límites de uso (Quotas)
  - Cada clínica tiene límites definidos según su plan
  - El sistema debe validar en tiempo real:
Ejemplo:
  - límite mensual: 1000 citas
  - citas actuales: 1000
  - Resultado:
    - no se pueden crear más citas
### 2.4 Estado de la clínica
  - Una clínica puede estar:
    - activa
    - suspendida
    - deshabilitada
  - Regla:
    - Si la clínica no está activa:
      - el sistema debe bloquear el acceso completamente
      
## 3. Modelo de Datos (Conceptual)
`Entidades principales`
  - Clinic
    - id
    - name
    - status (active / suspended / disabled)
    - external_subscription_id (opcional, si se integra con sistema externo)
  - Domain
    - id
    - domain
    - clinic_id
    - Nota: Permite múltiples dominios por clínica
  - FeatureFlag
    - id
    - code (ej: module_laboratory)
  - ClinicFeature
    - clinic_id
    - feature_flag_id
    - enabled (true/false)
  - UsageMetric
    - id
    - clinic_id
    - metric (ej: appointments_monthly)
    - value
    - period (ej: 2026-03)

## 4. Consideraciones Técnicas
### 4.1 Estrategia Multi-Tenancy
- Modelo elegido:
  - Shared Database + tenant_id (clinic_id)
- Reglas obligatorias
  - Todos los modelos multi-tenant deben tener:
    - campo clinic_id (FK obligatorio)
    - No se permiten registros sin clínica
  - Se deben crear índices compuestos:
    - (clinic_id, id)
- Protección a nivel de base de datos
  - IMPORTANTE:
    - El aislamiento no debe depender solo del backend.
    - Se debe implementar:
      - Row Level Security (RLS) en PostgreSQL (Base de Datos a Utilizar)
  - Esto protege contra:
    - consultas raw()
    - errores en código
    - tareas asíncronas (Celery)
### 4.2 Base Model Obligatorio
- Todos los modelos deben heredar de una clase base (Ejemplo):
    class TenantModel(models.Model):
        clinic = ForeignKey(Clinic)

        class Meta:
            abstract = True
    Validación en escritura
    def save(self, *args, **kwargs):
        if not self.clinic_id:
            raise Exception("Clinic is required")   
### 4.3 ClinicGlobalManager (Aislamiento a nivel de Modelo)
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
- **Resumen:**
  - Aplica automáticamente el filtro por clínica
  - Evita errores humanos
  - Limitación:
    - No cubre:
      - relaciones inversas
      - prefetch_related
      - consultas complejas
    - Por eso NO es suficiente por sí solo
### 4.4 MultiDomainMiddleware (Identificación Dinámica de Clínicas)
- **Descripción:** 
    - Este componente es responsable de identificar qué clínica está realizando la solicitud al sistema.
    - Funciona como un motor de detección de inquilino (tenant) basado en el dominio o subdominio desde el cual se accede al sistema.
- **Funcionamiento:**
    - El middleware analiza el host del request HTTP y lo compara con los dominios registrados en el sistema para determinar a qué clínica pertenece la solicitud.
    - Una vez identificada la clínica:
        - se carga su configuración
        - se asocia al contexto de la petición
    - Se busca en tabla Domain
    - Se obtiene la clínica
    - Se adjunta al request
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
- **Mejoras obligatorias:**
    - **Cache (Redis):**
        - domain → clinic_id
    - **Validación de seguridad:**
        - lista blanca de dominios
        - evitar ataques por Host Header
    - **Falla segura:**
        - Si no se encuentra clínica:
            - NO se responde la solicitud
### 4.5 Aislamiento en API (ClinicIsolationMixin)
- **Descripción:** 
    - Se debe implementar un BaseViewSet obligatorio -> TODOS los endpoints de la API deben heredar de una misma clase base, donde centralizas la seguridad.
    - Su objetivo es garantizar que todas las consultas realizadas desde la API estén restringidas a la clínica correspondiente al usuario autenticado.
- **Validaciones:**
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
    - if request.user.clinic_id != request.clinic.id:
        raise PermissionDenied
- **Escritura segura:**
    - serializer.save(clinic=request.clinic)
- Ejemplo
    class BaseViewSet(ModelViewSet):

    def get_queryset(self):
        clinic = self.request.clinic

        if not clinic:
            return self.queryset.none()

        return self.queryset.filter(clinic=clinic)

    def perform_create(self, serializer):
        serializer.save(clinic=self.request.clinic)
### 4.6 DynamicBrandingEngine
- **Descripción:** 
    - Componente encargado de gestionar la identidad visual personalizada de cada clínica.
    - Este motor permite que el frontend obtenga la configuración visual correspondiente y la aplique dinámicamente.
- **Alcance:**
    - El motor permitirá gestionar:
    - Identidad visual: logotipos, isotipos y favicon por clínica.
    - Personalización de interfaz: definición de paleta de colores que el frontend aplicará dinámicamente.
    - Nomenclatura personalizada: posibilidad de modificar etiquetas utilizadas en la interfaz según la preferencia de cada clínica.
- **Endpoint:**
    - GET /api/branding/
- **Ejemplo:**
    {
      "logo": "https://cdn/logo.png",
      "primary_color": "#0A1AFF",
      "labels": {
        "patients": "Clientes"
      }
    }
- **Consideraciones:**
    - Uso de CDN (Content Delivery Network/Red de Distribución de Contenido) para imágenes (considerar futuramente)
    - Cache en frontend (localStorage)
### 4.7 Feature Toggling
- **Descripción:** 
    - Sistema encargado de activar o desactivar funcionalidades del sistema según el contrato comercial de cada clínica.
    - Cada funcionalidad del sistema puede controlarse mediante un interruptor lógico (feature flag).
- **Alcance:**
    - Esto permite habilitar módulos específicos sin necesidad de modificar el código ni desplegar nuevas versiones del sistema.
- **Flags Iniciales del Sistema:**
    - El sistema deberá considerar por defecto los siguientes módulos activables:
        - `module_psychology`: habilita evaluaciones psicológicas, baremos y notas de evolución mental.
        - `module_laboratory`: habilita la gestión de exámenes de laboratorio.
        - `module_imaging`: habilita estudios de diagnóstico por imágenes.
        - `module_nutrition`: habilita planes nutricionales y dietas.
        - `module_billing`: habilita facturación y cobros.
        - `module_inventory`: habilita control de stock de insumos.
        - `module_telemedicine`: habilita videoconsultas y telemedicina.
        - `module_reports`: habilita reportes y estadísticas avanzadas.
- **Validación backend obligatoria:**
    - if not clinic.has_feature("module_laboratory"):
        raise PermissionDenied
- **Extensibilidad:**
    - Permite agregar nuevos módulos sin cambiar arquitectura
### 4.8 Sistema de Quotas
- **Descripción:** 
    - Sistema encargado de gestionar límites de uso asociados al plan contratado.
    - Estos límites permiten controlar el consumo de recursos y establecer diferentes niveles de servicio.
- **Tabla de métricas:**
    - `usage_metrics`
- **Validación en tiempo real:**
    - if current_usage >= limit:
        bloquear_operacion()
- **Procesos adicionales:**
    - Jobs de reseteo mensual
    - Monitoreo de consumo  

## 5. Arquitectura de Plataforma
### 5.1 Separación de Sistemas
- **Control Plane (Sistema externo)**
    - Responsable de:
        - planes
        - suscripciones
        - pagos
        - activación/desactivación de clínicas
- **Application Plane (Sistema clínico)**
    - Responsable de:
        - operaciones médicas
        - pacientes
        - agenda
        - historia clínica
        - facturación
        - inventario
        - telemedicina
        - reportes
### 5.2 Integración entre sistemas
- **El sistema clínico debe consultar el estado de la clínica:**
    - Ejemplo:
    - GET /control-plane/clinic/{id}
    - Respuesta:
    - {
        "status": "active",
        "features": ["module_laboratory"],
        "limits": {
            "appointments": 1000
        }
    }
- **Regla crítica:**
    - Si el Control Plane indica que la clínica está inactiva:
        - el sistema clínico debe bloquear acceso

### 6. Casos Especiales / Edge Cases
- Clínica suspendida por falta de pago
- Cambio de plan en caliente
- Reducción de límites (downgrade)
- Dominio mal configurado
- Acceso sin contexto de clínica

### 7. Pendientes / Evolución
- Soporte para:
    - schema por tenant
    - multi-base de datos
- Feature marketplace
- Expansión a múltiples productos SaaS