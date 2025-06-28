from django import forms
from django.contrib.auth.models import Group, Permission
from applications.security.models import Module, GroupModulePermission


class GroupModulePermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar el campo de grupo
        self.fields['group'].widget.attrs.update({
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'id': 'group-select'
        })
        
        # Configurar el campo de módulo
        self.fields['module'].widget.attrs.update({
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'id': 'module-select'
        })
        
        # Configurar el campo de permisos como checkboxes
        self.fields['permissions'].widget = forms.CheckboxSelectMultiple(attrs={
            'class': 'permission-checkbox'
        })
        
        # Configurar el queryset de permisos de forma segura
        self._setup_permissions_queryset()

    def _setup_permissions_queryset(self):
        """Configura el queryset de permisos de forma segura"""
        try:
            # Si estamos editando y hay un módulo seleccionado
            if self.instance.pk and hasattr(self.instance, 'module') and self.instance.module:
                # Si hay permisos asociados al módulo, mostrar solo esos
                module_permissions = self.instance.module.permissions.all()
                if module_permissions.exists():
                    self.fields['permissions'].queryset = module_permissions.order_by('name')
                else:
                    # Si no hay permisos específicos del módulo, mostrar todos
                    self.fields['permissions'].queryset = Permission.objects.all().order_by('content_type__model', 'name')
            else:
                # Por defecto, mostrar todos los permisos pero organizados
                self.fields['permissions'].queryset = Permission.objects.all().order_by('content_type__model', 'name')
        except Exception as e:
            # En caso de error, mostrar todos los permisos
            self.fields['permissions'].queryset = Permission.objects.all().order_by('content_type__model', 'name')

    class Meta:
        model = GroupModulePermission
        fields = ['group', 'module', 'permissions']
        labels = {
            'group': 'Grupo',
            'module': 'Módulo',
            'permissions': 'Permisos',
        }
        help_texts = {
            'group': 'Selecciona el grupo al que asignar permisos',
            'module': 'Selecciona el módulo sobre el cual otorgar permisos',
            'permissions': 'Marca los permisos que tendrá este grupo sobre el módulo seleccionado',
        }

    def clean(self):
        cleaned_data = super().clean()
        group = cleaned_data.get('group')
        module = cleaned_data.get('module')
        
        if group and module:
            # Verificar si ya existe esta combinación (excluyendo la instancia actual)
            existing = GroupModulePermission.objects.filter(group=group, module=module)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'Ya existe una asignación de permisos para el grupo "{group}" y el módulo "{module}".'
                )
        
        return cleaned_data
