from django import forms
from applications.core.models import Empleado


class EmpleadoForm(forms.ModelForm):
    """Formulario para crear/editar empleados"""
    
    class Meta:
        model = Empleado
        fields = [
            'nombres', 'apellidos', 'cedula_ecuatoriana', 'dni',
            'fecha_nacimiento', 'cargo', 'sueldo', 'fecha_ingreso',
            'direccion', 'latitud', 'longitud', 'foto', 'activo'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
            'latitud': forms.NumberInput(attrs={'step': '0.000001'}),
            'longitud': forms.NumberInput(attrs={'step': '0.000001'}),
            'direccion': forms.Textarea(attrs={'rows': 2}),
            'sueldo': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'activo': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales
        optional_fields = ['dni', 'latitud', 'longitud', 'foto']
        for field in optional_fields:
            self.fields[field].required = False
        
        # Agregar clases de Tailwind CSS
        for field in self.fields:
            if field != 'activo':  # No aplicar estas clases al checkbox
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
                })
