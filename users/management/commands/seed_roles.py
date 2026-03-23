"""
Management command: seed_roles
Carga en base de datos los Capabilities and RoleTemplates base del sistema.
Req: 2_Usuarios_Permisos.md sec. 2.3 - Gobernanza de Roles
"""
from django.core.management.base import BaseCommand
from django.db import transaction


CAPABILITIES = [
    # Módulo: patient
    {"codename": "patient.record.read",    "description": "Ver historia clínica del paciente", "module": "patient"},
    {"codename": "patient.record.write",   "description": "Crear / editar historia clínica",   "module": "patient"},
    {"codename": "patient.list.view",      "description": "Listar pacientes de la clínica",     "module": "patient"},
    {"codename": "patient.consent.manage", "description": "Gestionar consentimientos",          "module": "patient"},

    # Módulo: appointment
    {"codename": "appointment.create",     "description": "Crear una cita",                    "module": "appointment"},
    {"codename": "appointment.cancel",     "description": "Cancelar una cita",                 "module": "appointment"},
    {"codename": "appointment.reschedule", "description": "Reprogramar una cita",              "module": "appointment"},
    {"codename": "appointment.list.view",  "description": "Ver agenda de citas",               "module": "appointment"},

    # Módulo: clinical
    {"codename": "clinical.note.write",    "description": "Crear / editar notas de sesión",    "module": "clinical"},
    {"codename": "clinical.note.read",     "description": "Leer notas de sesión",              "module": "clinical"},
    {"codename": "clinical.result.view",   "description": "Ver resultados médicos",            "module": "clinical"},
    {"codename": "clinical.result.upload", "description": "Subir resultados médicos",          "module": "clinical"},

    # Módulo: lab
    {"codename": "lab.result.view",        "description": "Ver resultados de laboratorio",     "module": "lab"},
    {"codename": "lab.result.upload",      "description": "Subir resultados de laboratorio",   "module": "lab"},

    # Módulo: admin
    {"codename": "admin.users.manage",     "description": "Gestionar usuarios de la clínica",  "module": "admin"},
    {"codename": "admin.roles.manage",     "description": "Gestionar roles de la clínica",     "module": "admin"},
    {"codename": "admin.clinic.settings",  "description": "Configurar ajustes de la clínica",  "module": "admin"},
    {"codename": "admin.reports.view",     "description": "Ver reportes y estadísticas",       "module": "admin"},

    # Módulo: occupational
    {"codename": "occupational.eval.create", "description": "Crear evaluación ocupacional",   "module": "occupational"},
    {"codename": "occupational.eval.view",   "description": "Ver evaluación ocupacional",     "module": "occupational"},

    # Módulo: b2b
    {"codename": "b2b.company.view",       "description": "Ver datos de su empresa (portal B2B)", "module": "b2b"},
    {"codename": "b2b.workers.view",       "description": "Consultar estado de evaluaciones de trabajadores", "module": "b2b"},
]

ROLE_TEMPLATES = {
    "ROLE_TEMPLATE_ADMIN": {
        "description": "Administrador de clínica. Acceso total a gestión y configuración.",
        "capabilities": [
            "patient.record.read", "patient.record.write", "patient.list.view", "patient.consent.manage",
            "appointment.create", "appointment.cancel", "appointment.reschedule", "appointment.list.view",
            "clinical.note.write", "clinical.note.read", "clinical.result.view", "clinical.result.upload",
            "lab.result.view", "lab.result.upload",
            "admin.users.manage", "admin.roles.manage", "admin.clinic.settings", "admin.reports.view",
            "occupational.eval.create", "occupational.eval.view",
        ],
    },
    "ROLE_TEMPLATE_DOCTOR": {
        "description": "Especialista / Médico tratante. Enfocado en atención clínica.",
        "capabilities": [
            "patient.record.read", "patient.record.write", "patient.list.view",
            "appointment.create", "appointment.cancel", "appointment.reschedule", "appointment.list.view",
            "clinical.note.write", "clinical.note.read", "clinical.result.view", "clinical.result.upload",
            "lab.result.view", "lab.result.upload",
            "occupational.eval.create", "occupational.eval.view",
        ],
    },
    "ROLE_TEMPLATE_NURSE": {
        "description": "Enfermero/a. Soporte de atención clínica y triage.",
        "capabilities": [
            "patient.record.read", "patient.list.view",
            "appointment.list.view",
            "clinical.note.read", "clinical.result.view",
            "lab.result.view",
        ],
    },
    "ROLE_TEMPLATE_RECEPTION": {
        "description": "Recepcionista. Gestión de citas y registro de pacientes.",
        "capabilities": [
            "patient.list.view", "patient.consent.manage",
            "appointment.create", "appointment.cancel", "appointment.reschedule", "appointment.list.view",
        ],
    },
    "ROLE_TEMPLATE_SUPERVISOR": {
        "description": "Supervisor. Acceso a reportes y revisión de actividad.",
        "capabilities": [
            "patient.list.view",
            "appointment.list.view",
            "clinical.note.read", "clinical.result.view",
            "lab.result.view",
            "admin.reports.view",
            "occupational.eval.view",
        ],
    },
}


class Command(BaseCommand):
    help = "Carga Capabilities y RoleTemplates base del sistema (idempotente)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra qué se crearía sin persistir nada.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        from users.models import Capability, RoleTemplate

        dry_run = options["dry_run"]
        prefix = "[DRY-RUN] " if dry_run else ""

        self.stdout.write(self.style.MIGRATE_HEADING(f"{prefix}=== Cargando Capabilities ==="))

        # ── Capabilities ────────────────────────────────────────────────────────
        cap_objects = {}
        created_caps = 0
        for cap_data in CAPABILITIES:
            if dry_run:
                exists = Capability.objects.filter(codename=cap_data["codename"]).exists()
                status = "EXISTE" if exists else "NUEVO"
                self.stdout.write(f"  [{status}] {cap_data['codename']}")
                cap_objects[cap_data["codename"]] = None
                continue

            cap, created = Capability.objects.get_or_create(
                codename=cap_data["codename"],
                defaults={
                    "description": cap_data["description"],
                    "module": cap_data["module"],
                },
            )
            cap_objects[cap_data["codename"]] = cap
            if created:
                created_caps += 1
                self.stdout.write(f"  {self.style.SUCCESS('+')} {cap.codename}")
            else:
                self.stdout.write(f"  {self.style.WARNING('=')} {cap.codename} (ya existe)")

        self.stdout.write(self.style.MIGRATE_HEADING(f"\n{prefix}=== Cargando RoleTemplates ==="))

        # ── RoleTemplates ────────────────────────────────────────────────────────
        created_templates = 0
        for name, data in ROLE_TEMPLATES.items():
            if dry_run:
                exists = RoleTemplate.objects.filter(name=name).exists()
                status = "EXISTE" if exists else "NUEVO"
                self.stdout.write(f"  [{status}] {name}  ({len(data['capabilities'])} permisos)")
                continue

            template, created = RoleTemplate.objects.get_or_create(
                name=name,
                defaults={"description": data["description"]},
            )
            if created:
                created_templates += 1
                self.stdout.write(f"  {self.style.SUCCESS('+')} {name}")
            else:
                self.stdout.write(f"  {self.style.WARNING('=')} {name} (ya existe)")

            # Sincronizar capabilities (añade sin quitar las ya existentes)
            caps_to_add = [
                cap_objects[c] for c in data["capabilities"] if cap_objects.get(c)
            ]
            template.capabilities.add(*caps_to_add)

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\n✅  Seed completado: {created_caps} capabilities y {created_templates} role templates creados."
            ))
        else:
            if dry_run:
                raise SystemExit(0)  # Salida limpia sin persistir
