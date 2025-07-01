"""
Script para verificar que el sistema esté configurado correctamente.
Ejecutar después de setup_initial_data.py para validar la configuración.

Ejecutar con: python manage.py shell < verificar_sistema.py
"""

import os
import django
from django.contrib.auth.models import Group, Permission

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proy_clinico.settings')
django.setup()

from applications.security.models import Menu, Module, GroupModulePermission, User

def verificar_menus():
    """Verificar que los menús estén creados correctamente"""
    print("🔍 Verificando Menús...")
    
    menus = Menu.objects.all().order_by('order')
    
    if menus.count() == 0:
        print("❌ No se encontraron menús. Ejecuta setup_initial_data.py primero.")
        return False
    
    print(f"✅ Se encontraron {menus.count()} menús:")
    for menu in menus:
        modules_count = menu.modules.count()
        print(f"   📁 {menu.name} ({modules_count} módulos) - Orden: {menu.order}")
    
    return True

def verificar_modulos():
    """Verificar que los módulos estén creados correctamente"""
    print("\n🔍 Verificando Módulos...")
    
    modules = Module.objects.all().order_by('menu__order', 'order')
    
    if modules.count() == 0:
        print("❌ No se encontraron módulos. Ejecuta setup_initial_data.py primero.")
        return False
    
    print(f"✅ Se encontraron {modules.count()} módulos:")
    
    current_menu = None
    for module in modules:
        if current_menu != module.menu.name:
            current_menu = module.menu.name
            print(f"\n   📁 {current_menu}:")
        
        status = "🟢 Activo" if module.is_active else "🔴 Inactivo"
        print(f"      📄 {module.name} ({module.url}) - {status}")
    
    return True

def verificar_grupos():
    """Verificar que los grupos estén creados correctamente"""
    print("\n🔍 Verificando Grupos/Roles...")
    
    groups = Group.objects.all().order_by('name')
    
    if groups.count() == 0:
        print("❌ No se encontraron grupos. Ejecuta setup_initial_data.py primero.")
        return False
    
    print(f"✅ Se encontraron {groups.count()} grupos:")
    for group in groups:
        users_count = group.user_set.count()
        modules_count = GroupModulePermission.objects.filter(group=group).count()
        print(f"   👥 {group.name} ({users_count} usuarios, {modules_count} módulos)")
    
    return True

def verificar_permisos():
    """Verificar que los permisos estén asignados correctamente"""
    print("\n🔍 Verificando Permisos...")
    
    group_permissions = GroupModulePermission.objects.all()
    
    if group_permissions.count() == 0:
        print("❌ No se encontraron permisos asignados. Ejecuta setup_initial_data.py primero.")
        return False
    
    print(f"✅ Se encontraron {group_permissions.count()} asignaciones de permisos:")
    
    # Agrupar por grupo
    groups = Group.objects.all()
    for group in groups:
        group_modules = GroupModulePermission.objects.filter(group=group)
        if group_modules.exists():
            print(f"\n   👥 {group.name}:")
            for gmp in group_modules:
                permissions_count = gmp.permissions.count()
                print(f"      📄 {gmp.module.name} ({permissions_count} permisos)")
    
    return True

def verificar_usuarios():
    """Verificar que los usuarios estén creados correctamente"""
    print("\n🔍 Verificando Usuarios...")
    
    users = User.objects.all().order_by('email')
    
    if users.count() == 0:
        print("❌ No se encontraron usuarios.")
        return False
    
    print(f"✅ Se encontraron {users.count()} usuarios:")
    
    for user in users:
        groups = user.groups.all()
        group_names = [g.name for g in groups]
        status = "🟢 Activo" if user.is_active else "🔴 Inactivo"
        super_status = "⭐ Superusuario" if user.is_superuser else ""
        
        print(f"   👤 {user.get_full_name} ({user.email}) - {status} {super_status}")
        if group_names:
            print(f"      Roles: {', '.join(group_names)}")
        else:
            print("      ⚠️  Sin roles asignados")
    
    return True

def verificar_acceso_admin():
    """Verificar que existe al menos un usuario administrador"""
    print("\n🔍 Verificando Acceso de Administrador...")
    
    # Verificar superusuarios
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        print(f"✅ Se encontraron {superusers.count()} superusuarios:")
        for user in superusers:
            print(f"   ⭐ {user.email}")
    
    # Verificar usuarios con rol de administrador
    admin_groups = Group.objects.filter(name__icontains='administrador')
    admin_users = User.objects.filter(groups__in=admin_groups).distinct()
    
    if admin_users.exists():
        print(f"✅ Se encontraron {admin_users.count()} usuarios administradores:")
        for user in admin_users:
            groups = [g.name for g in user.groups.filter(name__icontains='administrador')]
            print(f"   👑 {user.email} - {', '.join(groups)}")
    
    if not superusers.exists() and not admin_users.exists():
        print("❌ No se encontraron usuarios administradores.")
        return False
    
    return True

def verificar_configuracion_completa():
    """Verificar que la configuración esté completa"""
    print("\n🔍 Verificando Configuración Completa...")
    
    issues = []
    
    # Verificar que todos los grupos tengan módulos asignados
    groups_without_modules = []
    for group in Group.objects.all():
        if not GroupModulePermission.objects.filter(group=group).exists():
            groups_without_modules.append(group.name)
    
    if groups_without_modules:
        issues.append(f"Grupos sin módulos: {', '.join(groups_without_modules)}")
    
    # Verificar que todos los módulos estén activos
    inactive_modules = Module.objects.filter(is_active=False)
    if inactive_modules.exists():
        module_names = [m.name for m in inactive_modules]
        issues.append(f"Módulos inactivos: {', '.join(module_names)}")
    
    # Verificar que existan usuarios activos
    active_users = User.objects.filter(is_active=True)
    if not active_users.exists():
        issues.append("No hay usuarios activos")
    
    if issues:
        print("⚠️  Se encontraron algunos problemas:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ La configuración está completa y correcta")
        return True

def mostrar_resumen():
    """Mostrar resumen del sistema"""
    print("\n" + "="*50)
    print("📊 RESUMEN DEL SISTEMA")
    print("="*50)
    
    menus_count = Menu.objects.count()
    modules_count = Module.objects.count()
    groups_count = Group.objects.count()
    users_count = User.objects.count()
    permissions_count = GroupModulePermission.objects.count()
    
    print(f"📁 Menús: {menus_count}")
    print(f"📄 Módulos: {modules_count}")
    print(f"👥 Grupos/Roles: {groups_count}")
    print(f"👤 Usuarios: {users_count}")
    print(f"🔐 Asignaciones de Permisos: {permissions_count}")
    
    print("\n🔑 CREDENCIALES DE ACCESO:")
    print("Email: admin@saludtotal.com")
    print("Contraseña: admin123")
    
    print("\n🌐 ACCESO AL SISTEMA:")
    print("URL: http://127.0.0.1:8000/")
    print("Admin: http://127.0.0.1:8000/admin/")

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICACIÓN DEL SISTEMA SALUDTOTAL")
    print("="*50)
    
    verificaciones = [
        verificar_menus(),
        verificar_modulos(),
        verificar_grupos(),
        verificar_permisos(),
        verificar_usuarios(),
        verificar_acceso_admin(),
        verificar_configuracion_completa()
    ]
    
    exitosas = sum(verificaciones)
    total = len(verificaciones)
    
    print(f"\n📈 RESULTADO: {exitosas}/{total} verificaciones exitosas")
    
    if exitosas == total:
        print("🎉 ¡El sistema está configurado correctamente!")
        mostrar_resumen()
    else:
        print("⚠️  Hay algunos problemas que necesitan atención.")
        print("💡 Ejecuta setup_initial_data.py si no lo has hecho aún.")

if __name__ == "__main__":
    main()
