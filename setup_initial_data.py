"""
Script para configurar datos iniciales del sistema:
- Menús principales
- Módulos por menú
- Grupos/Roles
- Permisos por grupo y módulo
- Usuario administrador inicial

Ejecutar con: python manage.py shell < setup_initial_data.py
"""

import os
import django
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proy_clinico.settings')
django.setup()

from applications.security.models import Menu, Module, GroupModulePermission, User

def create_menus():
    """Crear menús principales del sistema"""
    menus_data = [
        {'name': 'Administración', 'icon': 'bi bi-gear-fill', 'order': 1},
        {'name': 'Pacientes', 'icon': 'bi bi-person-heart', 'order': 2},
        {'name': 'Doctores', 'icon': 'bi bi-person-badge-fill', 'order': 3},
        {'name': 'Atención Médica', 'icon': 'bi bi-hospital', 'order': 4},
        {'name': 'Finanzas', 'icon': 'bi bi-cash-coin', 'order': 5},
        {'name': 'Reportes', 'icon': 'bi bi-graph-up', 'order': 6},
    ]
    
    created_menus = {}
    for menu_data in menus_data:
        menu, created = Menu.objects.get_or_create(
            name=menu_data['name'],
            defaults={
                'icon': menu_data['icon'],
                'order': menu_data['order']
            }
        )
        created_menus[menu.name] = menu
        print(f"{'Creado' if created else 'Existe'} menú: {menu.name}")
    
    return created_menus

def create_modules(menus):
    """Crear módulos por cada menú"""
    modules_data = [
        # Módulos de Administración
        {'name': 'Usuarios', 'url': 'security/user_list/', 'menu': 'Administración', 'icon': 'bi bi-people-fill', 'order': 1, 'description': 'Gestión de usuarios del sistema'},
        {'name': 'Grupos y Roles', 'url': 'security/group_list/', 'menu': 'Administración', 'icon': 'bi bi-shield-check', 'order': 2, 'description': 'Administración de roles y permisos'},
        {'name': 'Menús', 'url': 'security/menu_list/', 'menu': 'Administración', 'icon': 'bi bi-list-ul', 'order': 3, 'description': 'Configuración de menús del sistema'},
        {'name': 'Módulos', 'url': 'security/module_list/', 'menu': 'Administración', 'icon': 'bi bi-grid-3x3-gap', 'order': 4, 'description': 'Gestión de módulos del sistema'},
        {'name': 'Permisos', 'url': 'security/group_module_permission_list/', 'menu': 'Administración', 'icon': 'bi bi-key-fill', 'order': 5, 'description': 'Asignación de permisos por rol'},
        
        # Módulos de Pacientes
        {'name': 'Lista de Pacientes', 'url': 'core/pacientes/', 'menu': 'Pacientes', 'icon': 'bi bi-person-lines-fill', 'order': 1, 'description': 'Registro y gestión de pacientes'},
        {'name': 'Tipos de Sangre', 'url': 'core/tipos_sangre/', 'menu': 'Pacientes', 'icon': 'bi bi-droplet-fill', 'order': 2, 'description': 'Gestión de tipos de sangre'},
        {'name': 'Fotos de Pacientes', 'url': 'core/fotos_paciente/', 'menu': 'Pacientes', 'icon': 'bi bi-camera-fill', 'order': 3, 'description': 'Gestión de fotografías de pacientes'},
        
        # Módulos de Doctores
        {'name': 'Lista de Doctores', 'url': 'core/doctores/', 'menu': 'Doctores', 'icon': 'bi bi-person-badge', 'order': 1, 'description': 'Registro y gestión de doctores'},
        {'name': 'Especialidades', 'url': 'core/especialidades/', 'menu': 'Doctores', 'icon': 'bi bi-award-fill', 'order': 2, 'description': 'Gestión de especialidades médicas'},
        {'name': 'Empleados', 'url': 'core/empleados/', 'menu': 'Doctores', 'icon': 'bi bi-person-workspace', 'order': 3, 'description': 'Gestión de empleados del centro médico'},
        {'name': 'Cargos', 'url': 'core/cargos/', 'menu': 'Doctores', 'icon': 'bi bi-briefcase-fill', 'order': 4, 'description': 'Gestión de cargos y posiciones'},
        
        # Módulos de Atención Médica
        {'name': 'Calendario Médico', 'url': 'doctor/calendario/', 'menu': 'Atención Médica', 'icon': 'bi bi-calendar-event', 'order': 1, 'description': 'Calendario de citas médicas'},
        {'name': 'Atenciones', 'url': 'doctor/atenciones/', 'menu': 'Atención Médica', 'icon': 'bi bi-clipboard2-pulse', 'order': 2, 'description': 'Registro de atenciones médicas'},
        {'name': 'Diagnósticos', 'url': 'core/diagnosticos/', 'menu': 'Atención Médica', 'icon': 'bi bi-file-medical', 'order': 3, 'description': 'Gestión de diagnósticos médicos'},
        {'name': 'Medicamentos', 'url': 'core/medicamentos/', 'menu': 'Atención Médica', 'icon': 'bi bi-capsule', 'order': 4, 'description': 'Catálogo de medicamentos'},
        
        # Módulos de Finanzas
        {'name': 'Pagos', 'url': 'doctor/pagos/', 'menu': 'Finanzas', 'icon': 'bi bi-credit-card-fill', 'order': 1, 'description': 'Gestión de pagos y facturación'},
        {'name': 'Gastos', 'url': 'core/gastos/', 'menu': 'Finanzas', 'icon': 'bi bi-receipt', 'order': 2, 'description': 'Control de gastos del centro médico'},
        
        # Módulos de Reportes
        {'name': 'Reportes Médicos', 'url': 'reportes/medicos/', 'menu': 'Reportes', 'icon': 'bi bi-file-earmark-medical', 'order': 1, 'description': 'Reportes de atenciones médicas'},
        {'name': 'Reportes Financieros', 'url': 'reportes/financieros/', 'menu': 'Reportes', 'icon': 'bi bi-graph-up-arrow', 'order': 2, 'description': 'Reportes financieros y estadísticas'},
    ]
    
    created_modules = {}
    for module_data in modules_data:
        menu = menus[module_data['menu']]
        module, created = Module.objects.get_or_create(
            url=module_data['url'],
            defaults={
                'name': module_data['name'],
                'menu': menu,
                'icon': module_data['icon'],
                'order': module_data['order'],
                'description': module_data['description'],
                'is_active': True
            }
        )
        created_modules[module.name] = module
        print(f"{'Creado' if created else 'Existe'} módulo: {module.name}")
    
    return created_modules

def create_groups():
    """Crear grupos/roles del sistema"""
    groups_data = [
        {'name': 'Super Administrador', 'description': 'Acceso completo al sistema'},
        {'name': 'Administrador', 'description': 'Administración general del sistema'},
        {'name': 'Doctor', 'description': 'Médicos del centro de salud'},
        {'name': 'Secretaria Médica', 'description': 'Personal administrativo médico'},
        {'name': 'Recepcionista', 'description': 'Personal de recepción y citas'},
        {'name': 'Contador', 'description': 'Personal financiero y contable'},
        {'name': 'Enfermera', 'description': 'Personal de enfermería'},
    ]
    
    created_groups = {}
    for group_data in groups_data:
        group, created = Group.objects.get_or_create(
            name=group_data['name']
        )
        created_groups[group.name] = group
        print(f"{'Creado' if created else 'Existe'} grupo: {group.name}")
    
    return created_groups

def assign_permissions(groups, modules):
    """Asignar permisos a grupos por módulo"""
    
    # Definir qué módulos puede acceder cada rol
    group_modules = {
        'Super Administrador': list(modules.keys()),  # Acceso a todo
        'Administrador': [
            'Usuarios', 'Grupos y Roles', 'Menús', 'Módulos', 'Permisos',
            'Lista de Pacientes', 'Tipos de Sangre', 'Fotos de Pacientes',
            'Lista de Doctores', 'Especialidades', 'Empleados', 'Cargos',
            'Pagos', 'Gastos', 'Reportes Médicos', 'Reportes Financieros'
        ],
        'Doctor': [
            'Lista de Pacientes', 'Fotos de Pacientes',
            'Calendario Médico', 'Atenciones', 'Diagnósticos', 'Medicamentos',
            'Reportes Médicos'
        ],
        'Secretaria Médica': [
            'Lista de Pacientes', 'Tipos de Sangre', 'Fotos de Pacientes',
            'Lista de Doctores', 'Especialidades', 'Empleados',
            'Calendario Médico', 'Atenciones', 'Pagos'
        ],
        'Recepcionista': [
            'Lista de Pacientes', 'Fotos de Pacientes',
            'Calendario Médico', 'Pagos'
        ],
        'Contador': [
            'Pagos', 'Gastos', 'Reportes Financieros'
        ],
        'Enfermera': [
            'Lista de Pacientes', 'Fotos de Pacientes',
            'Atenciones', 'Medicamentos'
        ]
    }
    
    # Obtener permisos básicos de Django
    view_permission = Permission.objects.filter(codename__startswith='view_').first()
    add_permission = Permission.objects.filter(codename__startswith='add_').first()
    change_permission = Permission.objects.filter(codename__startswith='change_').first()
    delete_permission = Permission.objects.filter(codename__startswith='delete_').first()
    
    basic_permissions = []
    if view_permission:
        basic_permissions.append(view_permission)
    if add_permission:
        basic_permissions.append(add_permission)
    if change_permission:
        basic_permissions.append(change_permission)
    
    # Asignar módulos a grupos
    for group_name, module_names in group_modules.items():
        group = groups[group_name]
        
        for module_name in module_names:
            if module_name in modules:
                module = modules[module_name]
                
                # Crear o obtener la relación grupo-módulo
                group_module_permission, created = GroupModulePermission.objects.get_or_create(
                    group=group,
                    module=module
                )
                
                # Asignar permisos básicos
                if basic_permissions:
                    group_module_permission.permissions.set(basic_permissions)
                    
                    # Para Super Administrador, agregar también delete
                    if group_name == 'Super Administrador' and delete_permission:
                        group_module_permission.permissions.add(delete_permission)
                
                print(f"{'Creada' if created else 'Actualizada'} relación: {group.name} -> {module.name}")

def create_superuser():
    """Crear usuario administrador inicial"""
    if not User.objects.filter(email='admin@saludtotal.com').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@saludtotal.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        
        # Asignar al grupo Super Administrador
        super_admin_group = Group.objects.get(name='Super Administrador')
        admin_user.groups.add(super_admin_group)
        
        print(f"Usuario administrador creado: {admin_user.email}")
    else:
        print("Usuario administrador ya existe")

def main():
    """Función principal para ejecutar todo el setup"""
    print("=== CONFIGURACIÓN INICIAL DEL SISTEMA ===\n")
    
    print("1. Creando menús...")
    menus = create_menus()
    print()
    
    print("2. Creando módulos...")
    modules = create_modules(menus)
    print()
    
    print("3. Creando grupos/roles...")
    groups = create_groups()
    print()
    
    print("4. Asignando permisos...")
    assign_permissions(groups, modules)
    print()
    
    print("5. Creando usuario administrador...")
    create_superuser()
    print()
    
    print("=== CONFIGURACIÓN COMPLETADA ===")
    print("\nCredenciales del administrador:")
    print("Email: admin@saludtotal.com")
    print("Contraseña: admin123")
    print("\nPuedes cambiar estas credenciales después del primer login.")

if __name__ == "__main__":
    main()
