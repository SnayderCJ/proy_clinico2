#!/usr/bin/env python
"""
Script para configurar datos básicos del sistema SaludTotal
"""
import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proy_clinico.settings")
django.setup()

from django.contrib.auth.models import Group, Permission
from applications.security.models import User, Menu, Module, GroupModulePermission
from applications.core.models import TipoSangre, Especialidad, Paciente, Doctor


def create_basic_data():
    print("🔧 Configurando datos básicos del sistema...")

    # 1. Crear Menús
    print("📋 Creando menús...")
    menu_core, created = Menu.objects.get_or_create(
        name="Gestión Clínica", defaults={"icon": "bi bi-hospital", "order": 1}
    )
    if created:
        print(f"✅ Menú creado: {menu_core.name}")

    menu_doctor, created = Menu.objects.get_or_create(
        name="Atención Médica", defaults={"icon": "bi bi-heart-pulse", "order": 2}
    )
    if created:
        print(f"✅ Menú creado: {menu_doctor.name}")

    # 2. Crear Módulos
    print("🔧 Creando módulos...")

    # Módulo de Pacientes
    module_pacientes, created = Module.objects.get_or_create(
        url="core/pacientes/",
        defaults={
            "name": "Pacientes",
            "menu": menu_core,
            "description": "Gestión de pacientes",
            "icon": "bi bi-people",
            "order": 1,
        },
    )
    if created:
        print(f"✅ Módulo creado: {module_pacientes.name}")

    # Módulo de Calendario
    module_calendario, created = Module.objects.get_or_create(
        url="doctor/calendario/",
        defaults={
            "name": "Calendario",
            "menu": menu_doctor,
            "description": "Gestión de citas médicas",
            "icon": "bi bi-calendar",
            "order": 1,
        },
    )
    if created:
        print(f"✅ Módulo creado: {module_calendario.name}")

    # Módulo de Atenciones
    module_atenciones, created = Module.objects.get_or_create(
        url="doctor/atenciones/",
        defaults={
            "name": "Atenciones",
            "menu": menu_doctor,
            "description": "Registro de atenciones médicas",
            "icon": "bi bi-clipboard-heart",
            "order": 2,
        },
    )
    if created:
        print(f"✅ Módulo creado: {module_atenciones.name}")

    # Módulo de Pagos
    module_pagos, created = Module.objects.get_or_create(
        url="doctor/pagos/",
        defaults={
            "name": "Pagos",
            "menu": menu_doctor,
            "description": "Gestión de pagos",
            "icon": "bi bi-credit-card",
            "order": 3,
        },
    )
    if created:
        print(f"✅ Módulo creado: {module_pagos.name}")

    # 3. Crear Grupos
    print("👥 Creando grupos...")
    grupo_admin, created = Group.objects.get_or_create(name="Administradores")
    if created:
        print(f"✅ Grupo creado: {grupo_admin.name}")

    grupo_doctor, created = Group.objects.get_or_create(name="Doctores")
    if created:
        print(f"✅ Grupo creado: {grupo_doctor.name}")

    # 4. Asignar permisos a módulos
    print("🔐 Configurando permisos...")

    # Obtener permisos básicos
    permisos_basicos = Permission.objects.filter(
        codename__in=[
            "add_paciente",
            "change_paciente",
            "view_paciente",
            "delete_paciente",
        ]
    )

    # Asignar todos los módulos al grupo Administradores
    for module in [
        module_pacientes,
        module_calendario,
        module_atenciones,
        module_pagos,
    ]:
        gmp, created = GroupModulePermission.objects.get_or_create(
            group=grupo_admin, module=module
        )
        if created:
            print(f"✅ Permisos asignados: {grupo_admin.name} -> {module.name}")

        # Asignar permisos básicos
        gmp.permissions.set(permisos_basicos)

    # Asignar módulos médicos al grupo Doctores
    for module in [module_calendario, module_atenciones, module_pagos]:
        gmp, created = GroupModulePermission.objects.get_or_create(
            group=grupo_doctor, module=module
        )
        if created:
            print(f"✅ Permisos asignados: {grupo_doctor.name} -> {module.name}")

    # 5. Asignar usuario admin al grupo
    print("👤 Configurando usuario admin...")
    try:
        admin_user = User.objects.get(email="admin@gmail.com")
        admin_user.groups.add(grupo_admin)
        admin_user.is_superuser = True
        admin_user.save()
        print(f"✅ Usuario admin asignado al grupo: {grupo_admin.name}")
    except User.DoesNotExist:
        print("❌ Usuario admin@gmail.com no encontrado")

    # 6. Crear datos básicos de la clínica
    print("🏥 Creando datos básicos de la clínica...")

    # Tipos de sangre
    tipos_sangre = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
    for tipo in tipos_sangre:
        ts, created = TipoSangre.objects.get_or_create(
            tipo=tipo, defaults={"descripcion": f"Tipo de sangre {tipo}"}
        )
        if created:
            print(f"✅ Tipo de sangre creado: {tipo}")

    # Especialidades
    especialidades = [
        "Medicina General",
        "Cardiología",
        "Pediatría",
        "Ginecología",
        "Dermatología",
        "Neurología",
    ]
    for esp in especialidades:
        especialidad, created = Especialidad.objects.get_or_create(
            nombre=esp, defaults={"descripcion": f"Especialidad en {esp}"}
        )
        if created:
            print(f"✅ Especialidad creada: {esp}")

    print("\n🎉 ¡Configuración completada exitosamente!")
    print("📝 Resumen:")
    print(f"   - Menús: {Menu.objects.count()}")
    print(f"   - Módulos: {Module.objects.count()}")
    print(f"   - Grupos: {Group.objects.count()}")
    print(f"   - Tipos de sangre: {TipoSangre.objects.count()}")
    print(f"   - Especialidades: {Especialidad.objects.count()}")


if __name__ == "__main__":
    create_basic_data()
