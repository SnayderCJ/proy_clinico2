#!/usr/bin/env python
"""
Script para verificar usuarios en la base de datos
"""
import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proy_clinico.settings")
django.setup()

from applications.security.models import User


def check_users():
    print("🔍 VERIFICANDO USUARIOS EN LA BASE DE DATOS")
    print("=" * 50)

    users = User.objects.all()
    print(f"Total de usuarios: {users.count()}")

    for user in users:
        print(f"📧 Email: {user.email}")
        print(f"👤 Username: {user.username}")
        print(f"🏷️  Nombre: {user.get_full_name}")
        print(f"🔑 Es staff: {user.is_staff}")
        print(f"👥 Grupos: {[g.name for g in user.groups.all()]}")
        print("-" * 30)

    # Verificar usuario admin específico
    try:
        admin_user = User.objects.get(email="admin@saludtotal.com")
        print(f"✅ Usuario admin encontrado: {admin_user.email}")
        print(f"   Username: {admin_user.username}")
        print(f"   Activo: {admin_user.is_active}")
        print(f"   Staff: {admin_user.is_staff}")

        # Verificar si la contraseña funciona
        if admin_user.check_password("admin123"):
            print("✅ Contraseña admin123 es correcta")
        else:
            print("❌ Contraseña admin123 NO es correcta")

    except User.DoesNotExist:
        print("❌ Usuario admin@saludtotal.com NO encontrado")


if __name__ == "__main__":
    check_users()
