from django import forms
from applications.core.models import Especialidad


class EspecialidadForm(forms.ModelForm):
    """Formulario para crear/editar especialidades médicas"""
    
    class Meta:
        model = Especialidad
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales
        self.fields['descripcion'].required = False
        
        # Agregar clases de Tailwind CSS
        for field in self.fields:
            if field != 'activo':  # No aplicar estas clases al checkbox
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
                })
