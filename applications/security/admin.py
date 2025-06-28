from django.contrib import admin

# security/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Menu, Module, GroupModulePermission, AuditUser

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'dni', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('dni', 'image', 'direction', 'phone')}),
    )

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'order')
    search_fields = ('name',)
    ordering = ('order', 'name')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'menu', 'is_active', 'order')
    list_filter = ('menu', 'is_active')
    search_fields = ('name', 'url', 'description')
    ordering = ('menu', 'order', 'name')

@admin.register(GroupModulePermission)
class GroupModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('group', 'module')
    list_filter = ('group', 'module')
    filter_horizontal = ('permissions',)

@admin.register(AuditUser)
class AuditUserAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tabla', 'registroid', 'accion', 'fecha', 'hora', 'estacion')
    list_filter = ('accion', 'tabla', 'fecha')
    search_fields = ('usuario__username', 'usuario__email', 'tabla', 'accion')
    readonly_fields = ('usuario', 'tabla', 'registroid', 'accion', 'fecha', 'hora', 'estacion')
    ordering = ('-fecha', '-hora')
