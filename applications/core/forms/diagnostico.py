from django import forms
from applications.core.models import Diagnostico


class DiagnosticoForm(forms.ModelForm):
    """Formulario para crear/editar diagnósticos"""
    
    class Meta:
        model = Diagnostico
        fields = ['codigo', 'descripcion', 'datos_adicionales', 'activo']
        widgets = {
            'datos_adicionales': forms.Textarea(attrs={'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales
        self.fields['datos_adicionales'].required = False
        
        # Agregar clases de Tailwind CSS
        for field in self.fields:
            if field != 'activo':  # No aplicar estas clases al checkbox
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
                })

    def clean_codigo(self):
        """Validar que el código tenga el formato correcto"""
        codigo = self.cleaned_data['codigo']
        # Verificar que el código tenga el formato correcto (ejemplo: A09, J00, K35.2)
        if not codigo.replace('.', '').isalnum():
            raise forms.ValidationError(
                "El código debe contener solo letras, números y punto. Ejemplo: A09, J00, K35.2"
            )
        return codigo
