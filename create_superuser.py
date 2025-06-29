#!/usr/bin/env python
"""
Script para crear un superusuario
"""
import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proy_clinico.settings")
django.setup()

from applications.security.models import User


def create_superuser():
    try:
        # Intentar crear el superusuario
        superuser = User.objects.create_superuser(
            username="admin",
            email="admin@saludtotal.com",
            password="admin123",
            first_name="Administrador",
            last_name="Sistema",
        )
        print("✅ Superusuario creado exitosamente:")
        print(f"Email: {superuser.email}")
        print(f"Username: {superuser.username}")
        print(f"Password: admin123")
    except Exception as e:
        print(f"❌ Error al crear superusuario: {str(e)}")
        # Si el usuario ya existe, intentar actualizar la contraseña
        try:
            user = User.objects.get(email="admin@saludtotal.com")
            user.set_password("admin123")
            user.save()
            print("✅ Contraseña actualizada para el usuario existente")
        except User.DoesNotExist:
            print("❌ No se pudo encontrar el usuario para actualizar")


if __name__ == "__main__":
    create_superuser()
