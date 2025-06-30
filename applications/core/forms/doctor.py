from django import forms
from applications.core.models import Doctor


class DoctorForm(forms.ModelForm):
    """Formulario para crear/editar doctores"""
    
    class Meta:
        model = Doctor
        fields = [
            'nombres', 'apellidos', 'ruc', 'fecha_nacimiento',
            'direccion', 'latitud', 'longitud', 'codigo_unico_doctor',
            'especialidad', 'telefonos', 'email', 'horario_atencion',
            'duracion_atencion', 'curriculum', 'firma_digital', 'foto',
            'imagen_receta', 'activo'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'latitud': forms.NumberInput(attrs={'step': '0.000001'}),
            'longitud': forms.NumberInput(attrs={'step': '0.000001'}),
            'direccion': forms.Textarea(attrs={'rows': 2}),
            'horario_atencion': forms.Textarea(attrs={'rows': 3}),
            'duracion_atencion': forms.NumberInput(attrs={'min': '15', 'max': '120', 'step': '15'}),
            'activo': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales
        optional_fields = ['latitud', 'longitud', 'email', 'curriculum', 
                         'firma_digital', 'foto', 'imagen_receta']
        for field in optional_fields:
            self.fields[field].required = False
        
        # Agregar clases de Tailwind CSS
        for field in self.fields:
            if field != 'activo':  # No aplicar estas clases al checkbox
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
                })

        # Personalizar el widget de especialidades múltiples
        self.fields['especialidad'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
            'size': '5'  # Mostrar 5 opciones a la vez
        })
