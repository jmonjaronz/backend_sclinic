# Modelo Base de Identidad del Sistema

## Descripción:
- El sistema debe establecer una estructura base para la gestión de identidades que permita soportar múltiples contextos de uso (clínico, paciente, empresarial).
- Esta estructura define cómo una misma persona puede interactuar con el sistema en diferentes roles y portales.
## Definiciones:
- Persona
  - Representa a un individuo real dentro del sistema.
  - Es la entidad base sobre la cual se construyen los demás conceptos.
  - Puede existir sin tener acceso al sistema.
- Usuario
  - Representa una identidad de acceso digital asociada a una Persona.
  - Permite autenticarse en uno o más portales del sistema.
- Paciente
  - Representa el rol clínico de una Persona dentro de una clínica específica.
- Personal de Clínica   
  - Representa a una Persona que opera dentro de la clínica (médico, administrativo, etc.).
## Reglas:
- Una Persona puede tener múltiples roles dentro de una misma clínica.
- Una Persona puede ser simultáneamente:
  - paciente
  - usuario del sistema
  - personal de la clínica
  - responsable de dependientes
- Una Persona puede existir sin tener un Usuario asociado.