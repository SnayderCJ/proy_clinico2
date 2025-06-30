from django import forms
from applications.core.models import TipoMedicamento, MarcaMedicamento, Medicamento
from applications.core.utils.medicamento import ViaAdministracion


class TipoMedicamentoForm(forms.ModelForm):
    """Formulario para crear/editar tipos de medicamentos"""
    
    class Meta:
        model = TipoMedicamento
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


class MarcaMedicamentoForm(forms.ModelForm):
    """Formulario para crear/editar marcas de medicamentos"""
    
    class Meta:
        model = MarcaMedicamento
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


class MedicamentoForm(forms.ModelForm):
    """Formulario para crear/editar medicamentos"""
    
    class Meta:
        model = Medicamento
        fields = [
            'tipo', 'marca_medicamento', 'nombre', 'descripcion',
            'concentracion', 'via_administracion', 'cantidad',
            'precio', 'comercial', 'foto', 'activo'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'via_administracion': forms.Select(choices=ViaAdministracion.choices),
            'cantidad': forms.NumberInput(attrs={'min': '0'}),
            'precio': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'comercial': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600'}),
            'activo': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales
        optional_fields = ['marca_medicamento', 'descripcion', 'concentracion', 'foto']
        for field in optional_fields:
            self.fields[field].required = False
        
        # Agregar clases de Tailwind CSS
        for field in self.fields:
            if field not in ['comercial', 'activo']:  # No aplicar estas clases a los checkboxes
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
                })
