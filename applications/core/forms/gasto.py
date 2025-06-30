from django import forms
from applications.core.models import TipoGasto, GastoMensual


class TipoGastoForm(forms.ModelForm):
    """Formulario para crear/editar tipos de gastos"""
    
    class Meta:
        model = TipoGasto
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


class GastoMensualForm(forms.ModelForm):
    """Formulario para crear/editar gastos mensuales"""
    
    class Meta:
        model = GastoMensual
        fields = ['tipo_gasto', 'fecha', 'valor', 'observacion']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'valor': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'observacion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales
        self.fields['observacion'].required = False
        
        # Agregar clases de Tailwind CSS
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            })

    def clean_valor(self):
        """Validar que el valor sea positivo"""
        valor = self.cleaned_data['valor']
        if valor <= 0:
            raise forms.ValidationError("El valor del gasto debe ser mayor a cero.")
        return valor
