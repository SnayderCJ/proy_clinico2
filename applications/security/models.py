import os
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, PermissionsMixin
from django.db import models
from django.db.models import UniqueConstraint

"""
Modelo Menu: Representa las categorías principales de navegación del sistema.
Cada menú agrupa varios módulos relacionados funcionalmente.

Ejemplos:
1. Ventas (icon: bi bi-cart, order: 1) - Agrupa módulos de clientes, facturación, cotizaciones
2. Inventario (icon: bi bi-box, order: 2) - Agrupa módulos de productos, stock, transferencias
3. Finanzas (icon: bi bi-cash-coin, order: 3) - Agrupa módulos financieros
"""
class Menu(models.Model):
   
    name = models.CharField(verbose_name='Nombre', max_length=150, unique=True)
    icon = models.CharField(verbose_name='Icono', max_length=100, default='bi bi-calendar-x-fill')
    order = models.PositiveSmallIntegerField(verbose_name='Orden', default=0)
    
    def __str__(self):
        return self.name

   
   
    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'
        ordering = ['order', 'name']


"""
Modelo Module: Representa funcionalidades específicas del sistema agrupadas por menú.
Cada módulo tiene una URL única y pertenece a un menú particular.

Ejemplos:
1. Clientes (url: clientes/, menu: Ventas) - Gestión de clientes
2. Facturación (url: facturacion/, menu: Ventas) - Emisión de facturas
3. Productos (url: productos/, menu: Inventario) - Catálogo de productos
"""
class Module(models.Model):
    url = models.CharField(verbose_name='Url', max_length=100, unique=True)
    name = models.CharField(verbose_name='Nombre', max_length=100)
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT, verbose_name='Menu', related_name='modules')
    description = models.CharField(verbose_name='Descripción', max_length=200, null=True, blank=True)
    icon = models.CharField(verbose_name='Icono', max_length=100, default='bi bi-x-octagon')
    is_active = models.BooleanField(verbose_name='Es activo', default=True)
    order = models.PositiveSmallIntegerField(verbose_name='Orden', default=0)
  
    permissions = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return f'{self.name} [{self.url}]'

    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering = ['menu', 'order', 'name']


"""
Modelo GroupModulePermission: Asocia grupos con módulos y define qué permisos
tiene cada grupo sobre cada módulo específico.

Ejemplos:
1. Vendedores - Clientes: permisos [view_client, add_client, change_client]
2. Contadores - Facturas: permisos [view_invoice, add_invoice, change_invoice]
3. Bodegueros - Stock: permisos [view_stock, add_stock, change_stock]
"""
class GroupModulePermissionManager(models.Manager):
    """ Obtiene los módulos con su respectivo menú del grupo requerido que estén activos """ 
    def get_group_module_permission_active_list(self, group_id):
        return self.select_related('module','module__menu').filter(
            group_id=group_id,
            module__is_active=True
        )
    
class GroupModulePermission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='Grupo', related_name='module_permissions')
    module = models.ForeignKey('security.Module', on_delete=models.PROTECT, verbose_name='Módulo', related_name='group_permissions')
    permissions = models.ManyToManyField(Permission, verbose_name='Permisos')
    # Manager personalizado (conserva toda la funcionalidad del manager por defecto)
    objects = GroupModulePermissionManager()
    def __str__(self):
        return f"{self.module.name} - {self.group.name}"

    class Meta:
        verbose_name = 'Grupo módulo permiso'
        verbose_name_plural = 'Grupos módulos permisos'
        ordering = ['group', 'module']
        constraints = [
            UniqueConstraint(fields=['group', 'module'], name='unique_group_module')
        ]

"""
Modelo AuditUser: Registra las acciones realizadas por los usuarios en el sistema.
Cada registro incluye el usuario, la tabla afectada, el ID del registro, la acción realizada,
la fecha y hora, y la dirección IP desde donde se realizó la acción.

Ejemplos:
1. Usuario admin modificó el registro 123 de la tabla Pacientes el 2024-01-15
2. Usuario jperez eliminó el registro 456 de la tabla Pagos el 2024-01-16
"""
class AuditUser(models.Model):
    usuario = models.ForeignKey(
        'security.User',
        on_delete=models.PROTECT,
        verbose_name="Usuario",
        help_text="Usuario que realizó la acción"
    )
    tabla = models.CharField(
        max_length=100,
        verbose_name="Tabla",
        help_text="Nombre de la tabla afectada"
    )
    registroid = models.IntegerField(
        verbose_name="ID del Registro",
        help_text="ID del registro afectado"
    )
    accion = models.CharField(
        max_length=50,
        verbose_name="Acción",
        help_text="Tipo de acción realizada (ej: ADICION, MODIFICACION, ELIMINACION)"
    )
    fecha = models.DateField(
        verbose_name="Fecha",
        help_text="Fecha en que se realizó la acción"
    )
    hora = models.TimeField(
        verbose_name="Hora",
        help_text="Hora en que se realizó la acción"
    )
    estacion = models.CharField(
        max_length=100,
        verbose_name="Estación",
        help_text="Dirección IP desde donde se realizó la acción"
    )

    def __str__(self):
        return f"{self.usuario} - {self.accion} en {self.tabla} #{self.registroid}"

    class Meta:
        verbose_name = "Auditoría de Usuario"
        verbose_name_plural = "Auditorías de Usuarios"
        ordering = ['-fecha', '-hora']

"""
Modelo User: Extiende el usuario estándar de Django para añadir campos personalizados.
Utiliza email como identificador principal para login en lugar del username.

Ejemplos:
1. admin (email: admin@empresa.com) - Administrador del sistema
2. jperez (email: jperez@empresa.com) - Usuario con roles de Vendedor y Contador
3. mgarcia (email: mgarcia@empresa.com) - Usuario con roles de Contador y Auditor
"""
class User(AbstractUser, PermissionsMixin):
    dni = models.CharField(verbose_name='Cédula o RUC', max_length=13, blank=True, null=True)
    image = models.ImageField(
        verbose_name='Imagen de perfil',
        upload_to='security/users/',
        max_length=1024,
        blank=True,
        null=True
    )
    
    email = models.EmailField('Email', unique=True)
    direction = models.CharField('Dirección', max_length=200, blank=True, null=True)
    phone = models.CharField('Teléfono', max_length=50, blank=True, null=True)
  
 
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        permissions = (
            ("change_userprofile", "Cambiar perfil de Usuario"),
            ("change_userpassword", "Cambiar contraseña de Usuario"),
        )
    
    # def save(self, *args, **kwargs):
    #     def password_needs_hashing(password):
    #         # Detecta si la contraseña ya está hasheada
    #         return not password.startswith('pbkdf2_') and not password.startswith('argon2') and not password.startswith('bcrypt')

    #     if self.pk is None:
    #         if password_needs_hashing(self.password):
    #             self.set_password(self.password)
    #     else:
    #         old = User.objects.get(pk=self.pk)
    #         if self.password != old.password and password_needs_hashing(self.password):
    #             self.set_password(self.password)    #     super().save(*args, **kwargs)

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_groups(self):
        return self.groups.all()

    def get_short_name(self):
        return self.username

    # Métodos comentados temporalmente por errores de dependencias
    # def get_group_session(self):
    #     request = get_current_request()
    #     print("request==>",request)    #     return Group.objects.get(pk=request.session['group_id'])    # def set_group_session(self):
    #     request = get_current_request()
    #     if 'group' not in request.session:
    #         groups = request.user.groups.all().order_by('id')
    #         if groups.exists():
    #             request.session['group'] = groups.first()
    #             request.session['group_id'] = request.session['group'].id
    
    def get_image(self):
        """Devuelve la URL de la imagen de perfil del usuario o None si no tiene"""
        try:
            if self.image and hasattr(self.image, 'url'):
                # Verificar que el archivo existe físicamente
                if hasattr(self.image, 'path') and os.path.exists(self.image.path):
                    return self.image.url
                elif hasattr(self.image, 'url'):
                    # Para archivos en almacenamiento remoto o casos especiales
                    return self.image.url
        except (ValueError, OSError, AttributeError) as e:
            # Log del error para debugging si es necesario
            pass
        
        return None
