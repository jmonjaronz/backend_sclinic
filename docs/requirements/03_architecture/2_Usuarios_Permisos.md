# 🔐 Requerimiento Técnico: Identidad, Roles y Control de Acceso

## 1. Requerimiento Funcional
`Descripción`
Este módulo define el sistema de identidad y control de accesos del sistema clínico SaaS.
Su propósito es garantizar:
  - acceso seguro al sistema
  - control granular de permisos
  - protección de la información clínica
  - cumplimiento de normativa de privacidad
  - auditoría completa de accesos y modificaciones
Este módulo controla:
  - quién puede ingresar
  - qué puede ver
  - qué puede hacer

`Objetivos`
  - Gestionar identidades de usuarios de forma desacoplada
  - Permitir roles dinámicos por clínica
  - Controlar acciones mediante permisos granulares
  - Registrar accesos a datos sensibles
  - Validar consentimiento del paciente
  - Restringir acceso según tipo de portal

## 2. Reglas de Negocio
### 2.1 Identidad y contexto de clínica
- **El sistema debe separar explícitamente:**
  - Identidad (User) → credenciales de acceso
  - Contexto (Rol / Portal / Uso) → cómo se usa esa identidad
- **Reglas obligatorias**
  - Un usuario pertenece a una única clínica
  - No se permite compartir usuarios entre clínicas
  - El aislamiento de identidad es parte del modelo de seguridad
- **Identidad por contexto**
  - Un mismo individuo debe tener una única identidad (User) por clínica
    - Esta identidad puede operar en múltiples contextos:
    - paciente
    - staff clínico
    - portal empresarial (si aplica)
  - El sistema debe diferenciar:
    - identidad (User)
    - perfil (PatientProfile, StaffProfile, CompanyProfile)
    - contexto de sesión (portal + rol activo)
  - Ejemplo:
    - Contexto	                Usuario	                    Tipo
    - Paciente	                DNI: 12345678	            PATIENT
    - Intranet	                usuario: CGPT	            STAFF
    - B2B	                    usuario corporativo	        COMPANY
- **Regla crítica**
  - El sistema NO debe asumir que estos usuarios representan la misma persona
  - Si se necesita relación:
    - Debe ser explícita
    - Debe estar controlada (ej: tabla PersonLink opcional)
- **Contexto de sesión del usuario**
  - Aunque un usuario pertenece a una única clínica, el sistema debe permitir que opere en distintos contextos funcionales dentro de esa clínica.
  - Definición de contexto
    - Un contexto de sesión está compuesto por:
      - tipo de portal:
        - intranet clínica
        - portal paciente
        - portal empresarial (B2B)
      - rol activo (si aplica)
    - Reglas:
      - Un usuario puede tener acceso a múltiples portales dentro de la misma clínica.
      - El acceso a cada portal debe estar explícitamente habilitado.
      - El usuario solo puede operar bajo un contexto activo a la vez.
      - El contexto debe definirse al momento de autenticación o inmediatamente después.
    - Para acceder al portal paciente, el usuario debe estar vinculado explícitamente a un registro de paciente dentro de la clínica.
    - Esta vinculación debe ser validada mediante mecanismos de verificación (ej: identidad, contacto o validación administrativa).
### 2.2 Roles dinámicos
  - Roles definidos en base de datos
  - Un usuario puede tener múltiples roles
  - El sistema debe permitir definir un rol activo dentro del contexto de sesión.
  - Un usuario puede tener múltiples roles asignados.
  - El rol activo determina los permisos efectivos durante la sesión.
  - El cambio de rol activo puede permitirse durante la sesión según políticas de seguridad.

### 2.3 Gobernanza de Roles
  - Si cada clínica crea roles sin control → caos organizacional
  - **Plantillas base del sistema**
    - El sistema debe incluir roles predefinidos:
      - ROLE_TEMPLATE_ADMIN
      - ROLE_TEMPLATE_DOCTOR
      - ROLE_TEMPLATE_NURSE
      - ROLE_TEMPLATE_RECEPTION
      - ROLE_TEMPLATE_SUPERVISOR
    - Clonación editable
    - Las clínicas pueden:
      - copiar una plantilla
      - modificar permisos
      - renombrar el rol
    - Esto evita errores y acelera configuración
  - Restricción
    - No se permite crear roles sin permisos asignados
    - Validar en backend:
      - if role.permissions.count() == 0:
          raise ValidationError("El rol debe tener al menos un permiso.")
### 2.4 Permisos por capacidades
  - **Descripción**
    - El control de acceso se basará en un modelo de permisos por capacidades.
    - Cada permiso representa una acción específica dentro del sistema.
    - Los permisos se asignan a los roles y los roles se asignan a los usuarios.
    - Este modelo permite controlar con precisión qué acciones puede realizar cada usuario.
  - **Convención obligatoria**
    - Formato:
      - <modulo>.<recurso>.<accion>
    - Ejemplos:
      - patient.record.read
      - patient.record.update
      - appointment.create
      - appointment.cancel
      - lab.result.view
    - Relación con módulos (Feature Toggling)
    - Regla:
      - Si un módulo NO está activo:
        - sus permisos NO deben aplicarse
      - Ejemplo:
        - module_laboratory = false
        - todos los permisos lab.* quedan inválidos
    Formato:
      - <modulo>.<recurso>.<accion>
    Ejemplos:
      - patient.record.read
      - patient.record.update
      - appointment.create
      - appointment.cancel
      - lab.result.view
    - Relación con módulos (Feature Toggling)
    - Regla:
      - Si un módulo NO está activo:
        - sus permisos NO deben aplicarse
    - Ejemplo:
      - module_laboratory = false
      - todos los permisos lab.* quedan inválidos
### 2.5 Acceso a portales
  - Tipos de portales
    - Intranet	Staff clínico	Roles + permisos
    - Paciente	Pacientes	Solo su data
    - B2B	Empresas	Data restringida
  - Regla técnica
    - Cada request debe validar obligatoriamente:
      - clinic_id
      - portal_type
      - rol activo (si aplica)
      - permisos asociados
  - Reglas de acceso por portal:
    - Portal Intranet:
      - Requiere autenticación como usuario de tipo STAFF
      - Permisos controlados por roles
    - Portal Paciente:
      - Solo permite acceso a datos del paciente vinculado al usuario
      - No requiere roles administrativos
    - Portal B2B:
      - Acceso restringido a información autorizada por convenios
      - No permite acceso a historia clínica completa
- El acceso al portal paciente requiere:
  - vinculación explícita entre User y PatientProfile
- El acceso a dependientes requiere:
  - relación válida en PatientRelationship
- El backend debe validar:
  - identidad
  - vínculo
  - contexto
### 2.6 Consentimiento del paciente
  - No se puede:
    - crear historia clínica
    - ejecutar evaluaciones
    - mostrar datos médicos
  - si no existe consentimiento válido
### 2.7 Tipos de Usuario y Contexto de Uso
- El sistema NO define múltiples tipos de usuario a nivel de identidad.
- Existe una única entidad User.
- Los comportamientos se definen por:
  - perfiles asociados
  - roles
  - contexto de sesión
- Contextos soportados:
  - intranet (staff clínico)
  - patient_portal
  - b2b_portal
- Reglas:
  - Un usuario puede operar en múltiples contextos
  - El contexto activo define:
    - permisos
    - alcance de datos
- Ejemplo:
  - Usuario con:
    - StaffProfile (doctor)
    - PatientProfile
  - Puede:
    - acceder como doctor → ver pacientes
    - acceder como paciente → ver su historia

## 3. Modelo de Datos (Conceptual)
### 3.1 Entidades principales
  - User
    - identidad (login)
  - Role
    - definido por clínica
  - Permission
    - capacidad específica
  - RolePermission
    - relación rol → permisos
  - UserRole
    - usuario → roles
  - RoleTemplate
    - plantillas base del sistema
  - ClinicalAuditLog (Auditoría Clínica)
    - id
    - user_id
    - clinic_id
    - action (VIEW, CREATE, UPDATE, DELETE)
    - entity_type
    - entity_id
    - before (JSON)
    - after (JSON)
    - ip_address
    - user_agent
    - timestamp
  - Consent
    - id
    - patient_id
    - consent_type
    - granted (bool)
    - granted_at
    - expires_at
- Un usuario puede estar vinculado a:
  - su propio perfil de paciente
  - múltiples dependientes (hijos)
- Esta relación es obligatoria para acceso al portal paciente

## 4. Consideraciones Técnicas
### 4.1 IdentityCore
  - **Descripción**
    - Este componente gestiona la identidad digital de los usuarios del sistema.
    - El usuario representa únicamente la cuenta de acceso al sistema, no el perfil clínico o administrativo.
    - Esto permite separar la identidad de los distintos perfiles que pueden existir dentro del sistema.
  - **Separación entre Identidad y Perfil**
    - El sistema debe permitir que un mismo usuario opere en distintos contextos funcionales dentro de su clínica, definidos por:
      - portal de acceso
      - rol activo (si aplica)
    - Un usuario puede:
      - acceder como personal clínico (intranet)
      - acceder como paciente (portal paciente), si existe vinculación con un paciente
    - Estos contextos deben estar aislados a nivel de permisos y datos
    - Esta separación permite mantener el sistema desacoplado y flexible a largo plazo.
  - **Asociación con Clínica**
    - Todos los usuarios del sistema estarán asociados a una clínica específica dentro de la arquitectura multi-tenant.
    - Esto garantiza que:
        - la identidad siempre pertenece a un tenant
        - el acceso a datos se limite a la clínica correspondiente
### 4.2 Sistema de Roles
  - Roles definidos en DB
  - No hardcodeados
### 4.3 Permisos
  - Evaluación en backend obligatoria
  - Nunca confiar en frontend
### 4.4 Enforcement de permisos
  - Regla crítica
  - Toda acción sensible debe validar permisos:
    - if not user.has_permission("patient.record.read"):
        raise PermissionDenied
### 4.5 ClinicalAuditSystem
  - **Descripción**
    - Los sistemas clínicos deben ser completamente auditables debido a la naturaleza sensible de la información médica.
    - Este componente registra cada acceso a información clínica relevante dentro del sistema.
  - **Objetivos del sistema de auditoría**
    - El registro de accesos permite:
        - detectar accesos indebidos
        - investigar incidentes de seguridad
        - cumplir regulaciones de salud
        - mantener trazabilidad de acciones realizadas por usuarios
  - **Alcance obligatorio** 
    - Registrar:
        - accesos (VIEW)
        - creación (CREATE)
        - edición (UPDATE)
        - eliminación (DELETE)
  - **Nivel clínico (CRÍTICO)**
    - Se debe registrar:
        - quién accede a historia clínica
        - cuándo
        - desde qué IP
        - desde qué dispositivo (user_agent)
  - **Ejemplo real**
    - {
        "user": "doctor@clinica.com",
        "action": "VIEW",
        "entity": "PatientRecord",
        "entity_id": 123,
        "ip": "192.168.1.10",
        "timestamp": "2026-03-20T10:00:00"
      }
### 4.6 ConsentManagement
  - **Descripción**
    - Este componente permite gestionar el consentimiento legal del paciente para el uso de su información personal y médica.
    - Esto es requerido por la legislación de protección de datos personales.
  - **Validación obligatoria**
    - Antes de:
        - crear historia clínica
        - ejecutar evaluación
        - mostrar datos médicos
  - **Ejemplo**
    - if not patient.has_valid_consent("medical_data"):
        raise PermissionDenied("Consentimiento requerido")
### 4.7 Integración con Multi-Tenancy
  - Todas las entidades deben tener clinic_id
  - Auditoría también debe ser multi-tenant
  - Permisos se evalúan dentro de la clínica
### 4.8 Integración con Feature Toggling
  - Permisos dependen de módulos activos
  - Si módulo está deshabilitado:
    - permisos asociados no funcionan
### 5. Casos Especiales / Edge Cases
  - Usuario con múltiples roles
  - Eliminación de rol en uso
  - Permisos inconsistentes
  - Acceso a datos sin consentimiento
  - Usuario accediendo a otra clínica
  - Acceso desde portal incorrecto
### 6. Pendientes / Evolución
  - RBAC + ABAC (futuro)
  - Delegación de permisos
  - Auditoría avanzada (machine learning)
  - Consentimiento granular por tipo de dato
  - Integración con firma digital

## 7. Componente: PortalAccessControl (Extensión)
- **Descripción**
    - El sistema tendrá distintos portales de acceso diseñados para diferentes tipos de usuarios.
    - Cada portal tendrá restricciones específicas sobre la información que puede visualizar o gestionar.
- **Contexto de sesión obligatorio**
    - Todo acceso a un portal debe establecer un contexto de sesión válido que incluya:
        - usuario autenticado
        - clínica
        - portal
        - rol activo (si aplica)
- **Tipos de Portales**
    - El sistema deberá soportar al menos los siguientes contextos de acceso:
        - **Portal Intranet**
            - Utilizado por el personal clínico y administrativo de la clínica.
            - El acceso a información dependerá del rol activo del usuario y de los permisos asignados.

        - **Portal Paciente**
            - Permite que los pacientes consulten su información médica disponible dentro del sistema.
            - El acceso estará limitado únicamente a la información correspondiente al propio paciente.

        - **Portal Empresarial (B2B)**
            - Permite que empresas consulten el estado de evaluaciones ocupacionales de sus trabajadores.
            - Este portal tendrá restricciones estrictas que impiden el acceso a información clínica sensible como notas médicas o diagnósticos.  