# Modelo Entidad-Relación (E-R) - SCLINIC Backend

Este diagrama representa la estructura de datos actual del proyecto SCLINIC, organizada por módulos funcionales.

```mermaid
erDiagram
    %% Core & Users
    CLINIC ||--o{ HEADQUARTERS : "tiene"
    USER ||--o| SPECIALIST : "es perfil"
    USER ||--o| PATIENT : "es perfil (opcional)"
    
    %% Clinics Module
    HEADQUARTERS ||--o{ ROOM : "contiene"
    HEADQUARTERS ||--o{ SPECIALIST_SCHEDULE : "asigna"
    ROOM ||--o{ BED : "tiene"
    SPECIALTY ||--o{ SERVICE : "categoriza"
    SPECIALIST }|--|{ SPECIALTY : "pertenece"
    SPECIALIST }|--|{ SERVICE : "autorizado"
    SERVICE ||--o{ SERVICE_RESOURCE_REQUIREMENT : "requiere"
    
    %% Patients Module
    PATIENT ||--o| CLINICAL_RECORD : "tiene"
    PATIENT ||--o{ PATIENT_FAMILY_LINK : "relaciona"
    PATIENT ||--o{ PATIENT_INSURANCE : "cuenta con"
    PATIENT ||--o{ EMERGENCY_CONTACT : "tiene"
    
    %% Appointments Module
    APPOINTMENT }|--|| PATIENT : "para"
    APPOINTMENT }|--|| SERVICE : "de"
    APPOINTMENT ||--o| SESSION_NOTE : "genera (vínculo 1:1)"
    APPOINTMENT }|--o| SPECIALIST : "atendido por"
    APPOINTMENT_GROUP ||--o{ APPOINTMENT : "agrupa"
    TREATMENT_PLAN ||--o{ APPOINTMENT : "contiene sesiones"
    
    %% Companies & B2B
    COMPANY ||--o{ COMPANY_PROJECT : "tiene"
    COMPANY ||--o{ COMPANY_EMPLOYEE : "emplea"
    COMPANY ||--o{ AGREEMENT : "firma con clínica"
    AGREEMENT ||--o{ INSTITUTION_SERVICE_PRICE : "define precios"
    MEDICAL_PROTOCOL ||--o{ PROTOCOL_SERVICE : "incluye"
    COMPANY_EMPLOYEE ||--o{ EMPLOYEE_PROTOCOL_ASSIGNMENT : "se le asigna"
    
    %% Insurances
    INSURER ||--o{ INSURANCE_PLAN : "ofrece"
    INSURANCE_PLAN ||--o{ INSURANCE_COVERAGE : "define"
    PATIENT_INSURANCE }|--|| INSURANCE_PLAN : "usa"
    
    %% Clinical Records (HCE)
    CLINICAL_RECORD ||--o{ SESSION_NOTE : "contiene"
    SESSION_NOTE ||--o{ MEDICAL_ORDER : "genera"
    SESSION_NOTE ||--o{ PRESCRIPTION : "incluye"
    SESSION_NOTE ||--o{ EVOLUTION_NOTE : "puede ser"
    PRESCRIPTION ||--o{ PRESCRIPTION_ITEM : "contiene"
    
    %% Occupational Health
    OCCUPATIONAL_EVALUATION }|--|| PATIENT : "evalúa"
    OCCUPATIONAL_EVALUATION }|--|| COMPANY : "para"
    OCCUPATIONAL_EVALUATION ||--o{ EVALUATION_SERVICE_STATUS : "rastrea"
    OCCUPATIONAL_EVALUATION ||--o| APTITUDE_DICTUM : "resulta en"

    class CLINIC {
        uuid id
        string name
    }
    class USER {
        uuid id
        string username
        string role
    }
    class PATIENT {
        int id
        string document_number
        string first_name
    }
    class APPOINTMENT {
        uuid id
        date date
        string status
    }
    class SESSION_NOTE {
        uuid id
        json dynamic_data
        string diagnosis
    }
    class COMPANY {
        uuid id
        string ruc
        string razon_social
    }
```

## Resumen de Módulos

### Módulo `core` y `users`
- **Clinic**: La entidad raíz para el multi-tenancy.
- **User**: Usuarios del sistema con roles (Admin, Especialista, Paciente, Externo).

### Módulo `clinics`
- **Specialist**: Perfil profesional vinculado a un `User`.
- **Headquarters**: Sedes físicas de la clínica.
- **Service**: El catálogo de prestaciones (Consultas, Procedimientos, Exámenes).

### Módulo `patients`
- **Patient**: Datos demográficos y clínicos básicos.
- **PatientInsurance**: Relación activa entre un paciente y su seguro para esta clínica.

### Módulo `appointments`
- **Appointment**: La reserva de un servicio en un horario específico.
- **TreatmentPlan**: Un paquete de sesiones sugeridas para un paciente.

### Módulo `clinical_records` (HCE)
- **ClinicalRecord**: El expediente unificado.
- **SessionNote**: Notas de evolución, órdenes médicas y recetas.
- **HCETemplate**: Plantillas dinámicas (JSON Schema) para diferentes especialidades.

### Módulo `companies` & `occupational_health`
- **Company**: Empresas clientes B2B.
- **MedicalProtocol**: Paquetes de exámenes por puesto de trabajo.
- **OccupationalEvaluation**: La ejecución de un protocolo para un trabajador.
