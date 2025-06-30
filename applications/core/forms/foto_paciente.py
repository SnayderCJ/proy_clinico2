from django import forms
from applications.core.models import FotoPaciente


class FotoPacienteForm(forms.ModelForm):
    """Formulario para subir fotos de pacientes"""
    
    class Meta:
        model = FotoPaciente
        fields = ['paciente', 'imagen', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales
        self.fields['descripcion'].required = False
        
        # Agregar clases de Tailwind CSS
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            })

        # Personalizar el campo de imagen
        self.fields['imagen'].widget.attrs.update({
            'accept': 'image/*',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
        })

    def clean_imagen(self):
        """Validar el archivo de imagen"""
        imagen = self.cleaned_data.get('imagen')
        if imagen:
            # Verificar el tamaño del archivo (máximo 5MB)
            if imagen.size > 5 * 1024 * 1024:
                raise forms.ValidationError("El archivo no puede ser mayor a 5MB.")
            
            # Verificar el tipo de archivo
            if not imagen.content_type.startswith('image/'):
                raise forms.ValidationError("El archivo debe ser una imagen válida.")
        
        return imagen
