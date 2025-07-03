from django import forms
from applications.doctor.models import ServiciosAdicionales

class ServicioAdicionalForm(forms.ModelForm):
    class Meta:
        model = ServiciosAdicionales
        fields = ['nombre_servicio', 'costo_servicio', 'descripcion', 'activo']
        widgets = {
            'nombre_servicio': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg'}),
            'costo_servicio': forms.NumberInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg', 'step': '0.01'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600'})
        }
