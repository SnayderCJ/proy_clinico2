#!/usr/bin/env python
"""
Script para probar el sistema de roles creado
"""
import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proy_clinico.settings")
django.setup()

from django.contrib.auth.models import Group
from applications.security.models import User, Menu, Module, GroupModulePermission


def test_role_system():
    print("🧪 PROBANDO SISTEMA DE ROLES")
    print("=" * 50)

    # 1. Verificar usuarios creados
    print("\n👤 USUARIOS CREADOS:")
    users = User.objects.all()
    for user in users:
        groups = user.groups.all()
        print(f"  • {user.email} - Grupos: {[g.name for g in groups]}")

    # 2. Verificar grupos y sus módulos
    print("\n👥 GRUPOS Y SUS MÓDULOS:")
    groups = Group.objects.all()
    for group in groups:
        print(f"\n  📋 {group.name}:")
        gmps = GroupModulePermission.objects.filter(group=group)
        for gmp in gmps:
            print(f"    • {gmp.module.menu.name} > {gmp.module.name}")
            perms = gmp.permissions.all()
            if perms:
                print(f"      Permisos: {[p.codename for p in perms[:3]]}...")

    # 3. Verificar menús y módulos
    print("\n📋 MENÚS Y MÓDULOS:")
    menus = Menu.objects.all().order_by("order")
    for menu in menus:
        print(f"\n  🏷️  {menu.name} (Orden: {menu.order})")
        modules = Module.objects.filter(menu=menu, is_active=True).order_by("order")
        for module in modules:
            print(f"    • {module.name} - {module.url}")

    # 4. Probar acceso por rol
    print("\n🔐 PRUEBA DE ACCESO POR ROL:")

    # Probar con usuario doctor
    try:
        doctor_user = User.objects.get(email="dr.garcia@saludtotal.com")
        doctor_group = doctor_user.groups.first()
        if doctor_group:
            print(f"\n  👨‍⚕️ Doctor ({doctor_user.email}):")
            doctor_modules = GroupModulePermission.objects.filter(
                group=doctor_group, module__is_active=True
            )
            print(f"    Módulos disponibles: {doctor_modules.count()}")
            for gmp in doctor_modules[:5]:  # Mostrar solo los primeros 5
                print(f"    • {gmp.module.name}")
    except User.DoesNotExist:
        print("  ❌ Usuario doctor no encontrado")

    # Probar con usuario secretaria
    try:
        secretaria_user = User.objects.get(email="secretaria@saludtotal.com")
        secretaria_group = secretaria_user.groups.first()
        if secretaria_group:
            print(f"\n  👩‍💼 Secretaria ({secretaria_user.email}):")
            secretaria_modules = GroupModulePermission.objects.filter(
                group=secretaria_group, module__is_active=True
            )
            print(f"    Módulos disponibles: {secretaria_modules.count()}")
            for gmp in secretaria_modules[:5]:  # Mostrar solo los primeros 5
                print(f"    • {gmp.module.name}")
    except User.DoesNotExist:
        print("  ❌ Usuario secretaria no encontrado")

    print("\n✅ PRUEBA COMPLETADA")
    print("=" * 50)


if __name__ == "__main__":
    test_role_system()
