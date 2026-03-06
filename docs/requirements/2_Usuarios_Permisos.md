# 🔐 Requerimiento Técnico: Identidad, Roles y Control de Acceso
Este módulo define el sistema de identidad y control de accesos del sistema.
Su propósito es garantizar:
- acceso seguro al sistema
- control granular de permisos
- protección de la información clínica
- cumplimiento de normativa de privacidad
- auditoría de accesos a datos sensibles
Este módulo controla quién puede ingresar al sistema y qué información puede consultar o modificar.

## 1. Componente: IdentityCore (Sistema de Identidad)
- **Descripción**
    - Este componente gestiona la identidad digital de los usuarios del sistema.
    - El usuario representa únicamente la cuenta de acceso al sistema, no el perfil clínico o administrativo.
    - Esto permite separar la identidad de los distintos perfiles que pueden existir dentro del sistema.

- **Separación entre Identidad y Perfil**
    - El sistema debe permitir que un mismo usuario pueda estar asociado a distintos perfiles según el contexto del sistema (Solo Portal B2B y Portal Intranet).
    - Por ejemplo:
        - perfil de especialista
        - perfil administrativo
        - perfil empresarial
    - Esta separación permite mantener el sistema desacoplado y flexible a largo plazo.

- **Asociación con Clínica**
    - Todos los usuarios del sistema estarán asociados a una clínica específica dentro de la arquitectura multi-tenant.
    - Esto garantiza que:
        - la identidad siempre pertenece a un tenant
        - el acceso a datos se limite a la clínica correspondiente

## 2. Componente: Sistema de Roles Dinámicos
- **Descripción**
    - El sistema implementará un modelo de roles dinámicos definidos en base de datos, evitando estructuras rígidas definidas en el código.
    - Esto permite que cada clínica pueda definir su propia estructura organizacional dentro del sistema.

- **Flexibilidad Organizacional**
    - Cada clínica podrá crear roles adaptados a su funcionamiento interno.
    - Ejemplos de roles posibles:
        - Psicólogo Tratante
        - Médico Ocupacional
        - Evaluador Psicotécnico
        - Recepcionista
        - Supervisor Médico
        - Coordinador Clínico

- **Asignación de Roles**
    - Un usuario podrá tener uno o varios roles dentro de una misma clínica.
    - El sistema deberá permitir seleccionar el rol activo durante el proceso de autenticación cuando el usuario tenga múltiples roles asignados.
    - Esto permite cargar el contexto de permisos correspondiente.

## 3. Componente: Sistema de Permisos por Capacidades
- **Descripción**
    - El control de acceso se basará en un modelo de permisos por capacidades.
    - Cada permiso representa una acción específica dentro del sistema.
    - Los permisos se asignan a los roles y los roles se asignan a los usuarios.
    - Este modelo permite controlar con precisión qué acciones puede realizar cada usuario.

- **Beneficios del modelo**
    - Este enfoque permite:
        - mayor flexibilidad
        - roles personalizados por clínica
        - control detallado de acciones
        - expansión futura del sistema sin cambios estructurales

## 4. Componente: ClinicalAuditSystem (Auditoría de Acceso)
- **Descripción**
    - Los sistemas clínicos deben ser completamente auditables debido a la naturaleza sensible de la información médica.
    - Este componente registra cada acceso a información clínica relevante dentro del sistema.

- **Objetivos del sistema de auditoría**
    - El registro de accesos permite:
        - detectar accesos indebidos
        - investigar incidentes de seguridad
        - cumplir regulaciones de salud
        - mantener trazabilidad de acciones realizadas por usuarios

- **Alcance del registro**
    - El sistema deberá registrar accesos a recursos sensibles como:
        - historias clínicas
        - diagnósticos
        - resultados médicos
        - documentos clínicos
        - evaluaciones ocupacionales
    - El sistema identificará los recursos mediante un esquema genérico que permita auditar distintos tipos de entidades del sistema.

## 5. Componente: ConsentManagement (Gestión de Consentimientos)
- **Descripción**
    - Este componente permite gestionar el consentimiento legal del paciente para el uso de su información personal y médica.
    - Esto es requerido por la legislación de protección de datos personales.

- **Validación de consentimiento**
    - Antes de permitir el acceso a ciertos procesos clínicos, el sistema deberá verificar que el paciente ha otorgado su consentimiento correspondiente.
    - Esto incluye situaciones como:
        - apertura de historia clínica
        - realización de evaluaciones médicas
        - acceso al portal del paciente
    - Si el consentimiento no existe o no está vigente, el sistema deberá bloquear el proceso correspondiente.

## 6. Componente: PortalAccessControl (Control de Acceso por Portal)
- **Descripción**
    - El sistema tendrá distintos portales de acceso diseñados para diferentes tipos de usuarios.
    - Cada portal tendrá restricciones específicas sobre la información que puede visualizar o gestionar.

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