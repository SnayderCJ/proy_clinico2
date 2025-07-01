# 🏥 Guía de Configuración del Sistema SaludTotal

## 📋 Resumen del Sistema

Tu sistema clínico tiene una arquitectura de seguridad basada en:
- **Menús**: Categorías principales de navegación
- **Módulos**: Funcionalidades específicas agrupadas por menú
- **Roles/Grupos**: Perfiles de usuario con permisos específicos
- **Permisos**: Control granular de acceso por rol y módulo

## 🚀 Pasos para Configurar el Sistema

### 1. Ejecutar Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Configurar Datos Iniciales
```bash
python manage.py shell < setup_initial_data.py
```

Este script creará:
- ✅ 6 menús principales
- ✅ 18 módulos organizados por menú
- ✅ 7 roles diferentes
- ✅ Permisos asignados por rol
- ✅ Usuario administrador inicial

### 3. Crear Usuarios de Ejemplo
```bash
python manage.py shell < manage_users_roles.py
```

Este script creará usuarios para cada rol con credenciales de prueba.

### 4. Iniciar el Servidor
```bash
python manage.py runserver
```

## 👥 Roles y Permisos del Sistema

### 🔴 Super Administrador
- **Acceso**: Completo a todo el sistema
- **Módulos**: Todos los módulos disponibles
- **Usuario**: admin@saludtotal.com / admin123

### 🟠 Administrador
- **Acceso**: Administración general del sistema
- **Módulos**: 
  - Gestión de usuarios, roles y permisos
  - Pacientes y doctores
  - Finanzas y reportes
- **Usuario**: administrador@saludtotal.com / admin123

### 🔵 Doctor
- **Acceso**: Funciones médicas principales
- **Módulos**:
  - Lista de pacientes y fotos
  - Calendario médico y atenciones
  - Diagnósticos y medicamentos
  - Reportes médicos
- **Usuarios**: 
  - dr.martinez@saludtotal.com / doctor123
  - dra.lopez@saludtotal.com / doctor123

### 🟢 Secretaria Médica
- **Acceso**: Administración médica y pacientes
- **Módulos**:
  - Gestión de pacientes completa
  - Doctores y especialidades
  - Calendario y atenciones
  - Pagos
- **Usuario**: secretaria@saludtotal.com / secretaria123

### 🟡 Recepcionista
- **Acceso**: Recepción y citas
- **Módulos**:
  - Pacientes básico
  - Calendario médico
  - Pagos
- **Usuario**: recepcion@saludtotal.com / recepcion123

### 🟣 Contador
- **Acceso**: Área financiera
- **Módulos**:
  - Pagos y gastos
  - Reportes financieros
- **Usuario**: contador@saludtotal.com / contador123

### 🟤 Enfermera
- **Acceso**: Apoyo médico
- **Módulos**:
  - Pacientes y fotos
  - Atenciones médicas
  - Medicamentos
- **Usuario**: enfermera@saludtotal.com / enfermera123

## 🏗️ Estructura de Menús y Módulos

### 📊 Administración
- Usuarios
- Grupos y Roles
- Menús
- Módulos
- Permisos

### 👤 Pacientes
- Lista de Pacientes
- Tipos de Sangre
- Fotos de Pacientes

### 👨‍⚕️ Doctores
- Lista de Doctores
- Especialidades
- Empleados
- Cargos

### 🏥 Atención Médica
- Calendario Médico
- Atenciones
- Diagnósticos
- Medicamentos

### 💰 Finanzas
- Pagos
- Gastos

### 📈 Reportes
- Reportes Médicos
- Reportes Financieros

## 🔧 Personalización del Sistema

### Agregar Nuevos Módulos
1. Crear el módulo en el admin de Django
2. Asignarlo a un menú existente
3. Configurar permisos por rol

### Crear Nuevos Roles
1. Crear el grupo en Django Admin
2. Asignar módulos específicos
3. Configurar permisos granulares

### Modificar Permisos
1. Ir a "Permisos" en el menú Administración
2. Seleccionar grupo y módulo
3. Asignar permisos específicos

## 🐛 Solución de Problemas

### Error: 'str' object has no attribute 'is_authenticated'
✅ **Solucionado**: Se corrigió el template tag `get_user_role_name`

### Error: 404 en /auth/signin/
✅ **Solucionado**: Las URLs están configuradas correctamente en `/security/signin/`

### Usuario sin permisos
1. Verificar que el usuario tenga un grupo asignado
2. Verificar que el grupo tenga módulos asignados
3. Verificar que los módulos estén activos

## 📝 Comandos Útiles

### Crear Superusuario
```bash
python manage.py createsuperuser
```

### Acceder al Shell de Django
```bash
python manage.py shell
```

### Ver Usuarios y Roles
```python
from applications.security.models import User
from django.contrib.auth.models import Group

# Ver todos los usuarios
for user in User.objects.all():
    print(f"{user.email} - Grupos: {[g.name for g in user.groups.all()]}")

# Ver todos los grupos
for group in Group.objects.all():
    print(f"{group.name} - Usuarios: {group.user_set.count()}")
```

### Asignar Rol a Usuario
```python
from applications.security.models import User
from django.contrib.auth.models import Group

user = User.objects.get(email='usuario@ejemplo.com')
grupo = Group.objects.get(name='Doctor')
user.groups.add(grupo)
```

## 🔐 Seguridad

### Cambiar Contraseñas por Defecto
Después de la configuración inicial, cambiar todas las contraseñas por defecto:

1. Acceder como administrador
2. Ir a "Usuarios" en el menú Administración
3. Editar cada usuario y cambiar la contraseña

### Configurar Permisos Granulares
El sistema permite configurar permisos específicos por módulo:
- **view**: Ver información
- **add**: Crear nuevos registros
- **change**: Modificar registros existentes
- **delete**: Eliminar registros

## 📞 Soporte

Si necesitas ayuda adicional:
1. Revisa los logs del servidor Django
2. Verifica la configuración en el admin de Django
3. Consulta la documentación de los modelos en `applications/security/models.py`

---

**¡Tu sistema SaludTotal está listo para usar!** 🎉

Recuerda cambiar las credenciales por defecto y personalizar los permisos según las necesidades específicas de tu centro médico.
