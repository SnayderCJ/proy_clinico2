from django import forms
from applications.core.models import TipoSangre


class TipoSangreForm(forms.ModelForm):
    """Formulario para crear/editar tipos de sangre"""
    
    class Meta:
        model = TipoSangre
        fields = ['tipo', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases de Tailwind CSS
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            })
