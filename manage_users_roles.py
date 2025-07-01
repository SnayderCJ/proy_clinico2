"""
Script para gestionar usuarios y roles del sistema de manera interactiva.
Permite crear usuarios y asignarles roles específicos.

Ejecutar con: python manage.py shell < manage_users_roles.py
"""

import os
import django
from django.contrib.auth.models import Group

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proy_clinico.settings')
django.setup()

from applications.security.models import User

def create_sample_users():
    """Crear usuarios de ejemplo para cada rol"""
    
    users_data = [
        {
            'username': 'dr_martinez',
            'email': 'dr.martinez@saludtotal.com',
            'password': 'doctor123',
            'first_name': 'Carlos',
            'last_name': 'Martínez',
            'groups': ['Doctor'],
            'dni': '1234567890'
        },
        {
            'username': 'dra_lopez',
            'email': 'dra.lopez@saludtotal.com',
            'password': 'doctor123',
            'first_name': 'María',
            'last_name': 'López',
            'groups': ['Doctor'],
            'dni': '1234567891'
        },
        {
            'username': 'sec_garcia',
            'email': 'secretaria@saludtotal.com',
            'password': 'secretaria123',
            'first_name': 'Ana',
            'last_name': 'García',
            'groups': ['Secretaria Médica'],
            'dni': '1234567892'
        },
        {
            'username': 'recep_torres',
            'email': 'recepcion@saludtotal.com',
            'password': 'recepcion123',
            'first_name': 'Luis',
            'last_name': 'Torres',
            'groups': ['Recepcionista'],
            'dni': '1234567893'
        },
        {
            'username': 'cont_rodriguez',
            'email': 'contador@saludtotal.com',
            'password': 'contador123',
            'first_name': 'Carmen',
            'last_name': 'Rodríguez',
            'groups': ['Contador'],
            'dni': '1234567894'
        },
        {
            'username': 'enf_morales',
            'email': 'enfermera@saludtotal.com',
            'password': 'enfermera123',
            'first_name': 'Patricia',
            'last_name': 'Morales',
            'groups': ['Enfermera'],
            'dni': '1234567895'
        },
        {
            'username': 'admin_sistema',
            'email': 'administrador@saludtotal.com',
            'password': 'admin123',
            'first_name': 'Roberto',
            'last_name': 'Administrador',
            'groups': ['Administrador'],
            'dni': '1234567896'
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        # Verificar si el usuario ya existe
        if User.objects.filter(email=user_data['email']).exists():
            print(f"Usuario {user_data['email']} ya existe")
            continue
            
        # Crear el usuario
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            dni=user_data.get('dni', '')
        )
        
        # Asignar grupos
        for group_name in user_data['groups']:
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                print(f"Grupo '{group_name}' no existe")
        
        created_users.append(user)
        print(f"Usuario creado: {user.email} - Grupos: {', '.join(user_data['groups'])}")
    
    return created_users

def show_users_and_roles():
    """Mostrar todos los usuarios y sus roles"""
    print("\n=== USUARIOS Y ROLES ACTUALES ===")
    
    users = User.objects.all().order_by('email')
    
    for user in users:
        groups = user.groups.all()
        group_names = [group.name for group in groups]
        
        print(f"\n👤 {user.get_full_name} ({user.email})")
        print(f"   Username: {user.username}")
        if user.dni:
            print(f"   DNI: {user.dni}")
        print(f"   Roles: {', '.join(group_names) if group_names else 'Sin roles asignados'}")
        print(f"   Activo: {'Sí' if user.is_active else 'No'}")
        print(f"   Superusuario: {'Sí' if user.is_superuser else 'No'}")

def show_available_roles():
    """Mostrar todos los roles disponibles"""
    print("\n=== ROLES DISPONIBLES ===")
    
    groups = Group.objects.all().order_by('name')
    
    for group in groups:
        user_count = group.user_set.count()
        print(f"🔐 {group.name} ({user_count} usuarios)")

def create_custom_user():
    """Función para crear un usuario personalizado (para uso manual)"""
    print("\n=== CREAR USUARIO PERSONALIZADO ===")
    print("Esta función está disponible para uso manual en el shell de Django")
    print("Ejemplo de uso:")
    print("""
from applications.security.models import User
from django.contrib.auth.models import Group

# Crear usuario
user = User.objects.create_user(
    username='nuevo_usuario',
    email='usuario@ejemplo.com',
    password='contraseña123',
    first_name='Nombre',
    last_name='Apellido',
    dni='1234567890'
)

# Asignar rol
grupo = Group.objects.get(name='Doctor')
user.groups.add(grupo)
    """)

def main():
    """Función principal"""
    print("=== GESTIÓN DE USUARIOS Y ROLES ===\n")
    
    print("1. Mostrando roles disponibles...")
    show_available_roles()
    
    print("\n2. Creando usuarios de ejemplo...")
    created_users = create_sample_users()
    
    print(f"\n3. Se crearon {len(created_users)} usuarios nuevos")
    
    print("\n4. Mostrando todos los usuarios...")
    show_users_and_roles()
    
    print("\n=== GESTIÓN COMPLETADA ===")
    print("\nCredenciales de usuarios creados:")
    print("- Doctores: doctor123")
    print("- Secretaria: secretaria123") 
    print("- Recepcionista: recepcion123")
    print("- Contador: contador123")
    print("- Enfermera: enfermera123")
    print("- Administrador: admin123")
    
    create_custom_user()

if __name__ == "__main__":
    main()
