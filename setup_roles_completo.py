#!/usr/bin/env python
"""
Script para configurar el sistema completo de roles, permisos y menús para SaludTotal
Roles: Administrador, Doctor, Secretaria, Recepcionista
"""
import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proy_clinico.settings")
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from applications.security.models import User, Menu, Module, GroupModulePermission
from applications.core.models import (
    TipoSangre,
    Especialidad,
    Paciente,
    Doctor,
    Empleado,
    Cargo,
)


def create_complete_role_system():
    print("🏥 CONFIGURANDO SISTEMA COMPLETO DE ROLES - SALUDTOTAL")
    print("=" * 60)

    # 1. CREAR MENÚS PRINCIPALES
    print("\n📋 CREANDO MENÚS PRINCIPALES...")

    # Menú Administración
    menu_admin, created = Menu.objects.get_or_create(
        name="Administración", defaults={"icon": "bi bi-gear-fill", "order": 1}
    )
    if created:
        print(f"✅ Menú creado: {menu_admin.name}")

    # Menú Gestión Clínica
    menu_clinica, created = Menu.objects.get_or_create(
        name="Gestión Clínica", defaults={"icon": "bi bi-hospital", "order": 2}
    )
    if created:
        print(f"✅ Menú creado: {menu_clinica.name}")

    # Menú Atención Médica
    menu_medica, created = Menu.objects.get_or_create(
        name="Atención Médica", defaults={"icon": "bi bi-heart-pulse", "order": 3}
    )
    if created:
        print(f"✅ Menú creado: {menu_medica.name}")

    # Menú Recepción
    menu_recepcion, created = Menu.objects.get_or_create(
        name="Recepción", defaults={"icon": "bi bi-person-check", "order": 4}
    )
    if created:
        print(f"✅ Menú creado: {menu_recepcion.name}")

    # Menú Reportes
    menu_reportes, created = Menu.objects.get_or_create(
        name="Reportes", defaults={"icon": "bi bi-graph-up", "order": 5}
    )
    if created:
        print(f"✅ Menú creado: {menu_reportes.name}")

    # 2. CREAR MÓDULOS POR MENÚ
    print("\n🔧 CREANDO MÓDULOS...")

    # MÓDULOS DE ADMINISTRACIÓN
    modules_admin = [
        (
            "security/users/",
            "Usuarios",
            "Gestión de usuarios del sistema",
            "bi bi-people-fill",
            1,
        ),
        (
            "security/groups/",
            "Grupos y Roles",
            "Gestión de grupos y permisos",
            "bi bi-shield-check",
            2,
        ),
        (
            "core/empleados/",
            "Empleados",
            "Gestión de empleados",
            "bi bi-person-badge",
            3,
        ),
        ("core/doctores/", "Doctores", "Gestión de doctores", "bi bi-person-heart", 4),
        (
            "core/especialidades/",
            "Especialidades",
            "Gestión de especialidades médicas",
            "bi bi-clipboard-pulse",
            5,
        ),
        (
            "core/configuracion/",
            "Configuración",
            "Configuración del sistema",
            "bi bi-sliders",
            6,
        ),
    ]

    # MÓDULOS DE GESTIÓN CLÍNICA
    modules_clinica = [
        ("core/pacientes/", "Pacientes", "Gestión de pacientes", "bi bi-people", 1),
        (
            "core/historia-clinica/",
            "Historia Clínica",
            "Historias clínicas de pacientes",
            "bi bi-journal-medical",
            2,
        ),
        (
            "core/medicamentos/",
            "Medicamentos",
            "Gestión de medicamentos",
            "bi bi-capsule",
            3,
        ),
        (
            "core/diagnosticos/",
            "Diagnósticos",
            "Gestión de diagnósticos",
            "bi bi-clipboard-check",
            4,
        ),
    ]

    # MÓDULOS DE ATENCIÓN MÉDICA
    modules_medica = [
        (
            "doctor/calendario/",
            "Agenda Médica",
            "Calendario de citas médicas",
            "bi bi-calendar-heart",
            1,
        ),
        (
            "doctor/citas/",
            "Citas Médicas",
            "Gestión de citas",
            "bi bi-calendar-check",
            2,
        ),
        (
            "doctor/atenciones/",
            "Atenciones",
            "Registro de atenciones médicas",
            "bi bi-clipboard-heart",
            3,
        ),
        (
            "doctor/recetas/",
            "Recetas Médicas",
            "Emisión de recetas",
            "bi bi-prescription2",
            4,
        ),
        (
            "doctor/examenes/",
            "Órdenes de Examen",
            "Órdenes de exámenes médicos",
            "bi bi-file-medical",
            5,
        ),
    ]

    # MÓDULOS DE RECEPCIÓN
    modules_recepcion = [
        (
            "recepcion/citas/",
            "Agendar Citas",
            "Programación de citas",
            "bi bi-calendar-plus",
            1,
        ),
        (
            "recepcion/pacientes/",
            "Registro Pacientes",
            "Registro rápido de pacientes",
            "bi bi-person-plus",
            2,
        ),
        ("recepcion/pagos/", "Pagos", "Gestión de pagos", "bi bi-credit-card", 3),
        (
            "recepcion/sala-espera/",
            "Sala de Espera",
            "Control de sala de espera",
            "bi bi-hourglass-split",
            4,
        ),
    ]

    # MÓDULOS DE REPORTES
    modules_reportes = [
        (
            "reportes/pacientes/",
            "Reporte Pacientes",
            "Reportes de pacientes",
            "bi bi-file-earmark-text",
            1,
        ),
        (
            "reportes/citas/",
            "Reporte Citas",
            "Reportes de citas médicas",
            "bi bi-calendar-week",
            2,
        ),
        (
            "reportes/ingresos/",
            "Reporte Ingresos",
            "Reportes financieros",
            "bi bi-cash-stack",
            3,
        ),
        (
            "reportes/doctores/",
            "Reporte Doctores",
            "Reportes de actividad médica",
            "bi bi-person-lines-fill",
            4,
        ),
    ]

    # Crear todos los módulos
    all_modules = {}

    for menu, modules_list in [
        (menu_admin, modules_admin),
        (menu_clinica, modules_clinica),
        (menu_medica, modules_medica),
        (menu_recepcion, modules_recepcion),
        (menu_reportes, modules_reportes),
    ]:
        for url, name, description, icon, order in modules_list:
            module, created = Module.objects.get_or_create(
                url=url,
                defaults={
                    "name": name,
                    "menu": menu,
                    "description": description,
                    "icon": icon,
                    "order": order,
                },
            )
            if created:
                print(f"✅ Módulo creado: {name}")
            all_modules[url] = module

    # 3. CREAR GRUPOS/ROLES
    print("\n👥 CREANDO GRUPOS Y ROLES...")

    roles = [
        ("Administradores", "Acceso completo al sistema"),
        ("Doctores", "Acceso a funciones médicas"),
        ("Secretarias", "Gestión administrativa y clínica"),
        ("Recepcionistas", "Atención al cliente y citas"),
    ]

    groups = {}
    for role_name, description in roles:
        group, created = Group.objects.get_or_create(name=role_name)
        if created:
            print(f"✅ Grupo creado: {role_name}")
        groups[role_name] = group

    # 4. CONFIGURAR PERMISOS POR ROL
    print("\n🔐 CONFIGURANDO PERMISOS POR ROL...")

    # ADMINISTRADORES - Acceso total
    admin_modules = list(all_modules.values())

    # DOCTORES - Módulos médicos y consulta de pacientes
    doctor_modules = [
        all_modules["core/pacientes/"],
        all_modules["core/historia-clinica/"],
        all_modules["core/medicamentos/"],
        all_modules["core/diagnosticos/"],
        all_modules["doctor/calendario/"],
        all_modules["doctor/citas/"],
        all_modules["doctor/atenciones/"],
        all_modules["doctor/recetas/"],
        all_modules["doctor/examenes/"],
        all_modules["reportes/pacientes/"],
        all_modules["reportes/citas/"],
    ]

    # SECRETARIAS - Gestión administrativa y clínica
    secretaria_modules = [
        all_modules["core/pacientes/"],
        all_modules["core/historia-clinica/"],
        all_modules["core/empleados/"],
        all_modules["core/doctores/"],
        all_modules["recepcion/citas/"],
        all_modules["recepcion/pacientes/"],
        all_modules["recepcion/pagos/"],
        all_modules["reportes/pacientes/"],
        all_modules["reportes/citas/"],
        all_modules["reportes/ingresos/"],
    ]

    # RECEPCIONISTAS - Atención al cliente
    recepcionista_modules = [
        all_modules["core/pacientes/"],
        all_modules["recepcion/citas/"],
        all_modules["recepcion/pacientes/"],
        all_modules["recepcion/pagos/"],
        all_modules["recepcion/sala-espera/"],
    ]

    # Asignar módulos a grupos
    role_modules = {
        "Administradores": admin_modules,
        "Doctores": doctor_modules,
        "Secretarias": secretaria_modules,
        "Recepcionistas": recepcionista_modules,
    }

    # Obtener permisos básicos
    content_types = ContentType.objects.filter(
        model__in=[
            "paciente",
            "doctor",
            "empleado",
            "user",
            "especialidad",
            "medicamento",
        ]
    )

    all_permissions = Permission.objects.filter(content_type__in=content_types)

    for role_name, modules in role_modules.items():
        group = groups[role_name]

        for module in modules:
            gmp, created = GroupModulePermission.objects.get_or_create(
                group=group, module=module
            )

            if created:
                print(f"✅ Asignado: {role_name} -> {module.name}")

            # Asignar permisos según el rol
            if role_name == "Administradores":
                # Administradores tienen todos los permisos
                gmp.permissions.set(all_permissions)
            elif role_name == "Doctores":
                # Doctores pueden ver, agregar y cambiar (no eliminar)
                doctor_perms = all_permissions.filter(
                    codename__in=[
                        "view_paciente",
                        "add_paciente",
                        "change_paciente",
                        "view_doctor",
                        "view_empleado",
                        "view_especialidad",
                        "view_medicamento",
                        "add_medicamento",
                        "change_medicamento",
                    ]
                )
                gmp.permissions.set(doctor_perms)
            elif role_name == "Secretarias":
                # Secretarias pueden gestionar pacientes y empleados
                secretaria_perms = all_permissions.filter(
                    codename__in=[
                        "view_paciente",
                        "add_paciente",
                        "change_paciente",
                        "delete_paciente",
                        "view_doctor",
                        "add_doctor",
                        "change_doctor",
                        "view_empleado",
                        "add_empleado",
                        "change_empleado",
                        "view_user",
                        "add_user",
                        "change_user",
                    ]
                )
                gmp.permissions.set(secretaria_perms)
            else:  # Recepcionistas
                # Recepcionistas solo pueden ver y agregar pacientes
                recepcionista_perms = all_permissions.filter(
                    codename__in=[
                        "view_paciente",
                        "add_paciente",
                        "change_paciente",
                        "view_doctor",
                    ]
                )
                gmp.permissions.set(recepcionista_perms)

    # 5. CREAR USUARIOS DE EJEMPLO
    print("\n👤 CREANDO USUARIOS DE EJEMPLO...")

    usuarios_ejemplo = [
        {
            "email": "admin@saludtotal.com",
            "username": "admin",
            "first_name": "Administrador",
            "last_name": "Sistema",
            "password": "admin123",
            "groups": ["Administradores"],
            "is_superuser": True,
            "is_staff": True,
        },
        {
            "email": "dr.garcia@saludtotal.com",
            "username": "dr.garcia",
            "first_name": "Carlos",
            "last_name": "García",
            "password": "doctor123",
            "groups": ["Doctores"],
            "is_staff": True,
        },
        {
            "email": "secretaria@saludtotal.com",
            "username": "secretaria",
            "first_name": "María",
            "last_name": "López",
            "password": "secretaria123",
            "groups": ["Secretarias"],
            "is_staff": True,
        },
        {
            "email": "recepcion@saludtotal.com",
            "username": "recepcion",
            "first_name": "Ana",
            "last_name": "Martínez",
            "password": "recepcion123",
            "groups": ["Recepcionistas"],
            "is_staff": True,
        },
    ]

    for user_data in usuarios_ejemplo:
        user, created = User.objects.get_or_create(
            email=user_data["email"],
            defaults={
                "username": user_data["username"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "is_superuser": user_data.get("is_superuser", False),
                "is_staff": user_data.get("is_staff", False),
            },
        )

        if created:
            user.set_password(user_data["password"])
            user.save()
            print(f"✅ Usuario creado: {user.email}")

            # Asignar grupos
            for group_name in user_data["groups"]:
                group = groups[group_name]
                user.groups.add(group)
                print(f"   → Asignado al grupo: {group_name}")

    # 6. CREAR DATOS BÁSICOS
    print("\n🏥 CREANDO DATOS BÁSICOS...")

    # Tipos de sangre
    tipos_sangre = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
    for tipo in tipos_sangre:
        ts, created = TipoSangre.objects.get_or_create(
            tipo=tipo, defaults={"descripcion": f"Tipo de sangre {tipo}"}
        )
        if created:
            print(f"✅ Tipo de sangre: {tipo}")

    # Especialidades médicas
    especialidades = [
        ("Medicina General", "Atención médica general y preventiva"),
        ("Cardiología", "Especialidad del corazón y sistema cardiovascular"),
        ("Pediatría", "Atención médica infantil"),
        ("Ginecología", "Salud reproductiva femenina"),
        ("Dermatología", "Enfermedades de la piel"),
        ("Neurología", "Sistema nervioso"),
        ("Traumatología", "Lesiones del sistema musculoesquelético"),
        ("Oftalmología", "Enfermedades de los ojos"),
        ("Otorrinolaringología", "Oído, nariz y garganta"),
        ("Psiquiatría", "Salud mental"),
    ]

    for nombre, descripcion in especialidades:
        esp, created = Especialidad.objects.get_or_create(
            nombre=nombre, defaults={"descripcion": descripcion}
        )
        if created:
            print(f"✅ Especialidad: {nombre}")

    # Cargos para empleados
    cargos = [
        ("Médico General", "Médico de atención primaria"),
        ("Médico Especialista", "Médico con especialización"),
        ("Enfermera", "Profesional de enfermería"),
        ("Secretaria Médica", "Asistente administrativa"),
        ("Recepcionista", "Atención al cliente"),
        ("Administrador", "Gestión administrativa"),
        ("Auxiliar de Enfermería", "Apoyo en enfermería"),
    ]

    for nombre, descripcion in cargos:
        cargo, created = Cargo.objects.get_or_create(
            nombre=nombre, defaults={"descripcion": descripcion}
        )
        if created:
            print(f"✅ Cargo: {nombre}")

    # 7. RESUMEN FINAL
    print("\n" + "=" * 60)
    print("🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
    print("=" * 60)
    print(f"📋 Menús creados: {Menu.objects.count()}")
    print(f"🔧 Módulos creados: {Module.objects.count()}")
    print(f"👥 Grupos creados: {Group.objects.count()}")
    print(f"👤 Usuarios creados: {User.objects.count()}")
    print(f"🩸 Tipos de sangre: {TipoSangre.objects.count()}")
    print(f"🏥 Especialidades: {Especialidad.objects.count()}")
    print(f"💼 Cargos: {Cargo.objects.count()}")

    print("\n📝 USUARIOS DE ACCESO:")
    print("┌─────────────────────────────────────────────────────────┐")
    print("│ ROL             │ EMAIL                    │ PASSWORD   │")
    print("├─────────────────────────────────────────────────────────┤")
    print("│ Administrador   │ admin@saludtotal.com     │ admin123   │")
    print("│ Doctor          │ dr.garcia@saludtotal.com │ doctor123  │")
    print("│ Secretaria      │ secretaria@saludtotal.com│ secretaria123│")
    print("│ Recepcionista   │ recepcion@saludtotal.com │ recepcion123│")
    print("└─────────────────────────────────────────────────────────┘")

    print("\n🔐 PERMISOS POR ROL:")
    print("• ADMINISTRADORES: Acceso completo al sistema")
    print("• DOCTORES: Gestión médica, pacientes, atenciones")
    print("• SECRETARIAS: Gestión administrativa y clínica")
    print("• RECEPCIONISTAS: Atención al cliente y citas")

    print("\n✨ El sistema está listo para usar!")


if __name__ == "__main__":
    create_complete_role_system()
