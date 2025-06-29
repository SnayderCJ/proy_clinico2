from django import forms
from applications.core.models import Paciente
from applications.core.utils.paciente import SexoChoices, EstadoCivilChoices

class PacienteForm(forms.ModelForm):
    """Formulario para crear/editar pacientes"""
    
    class Meta:
        model = Paciente
        fields = [
            'nombres', 'apellidos', 'cedula_ecuatoriana', 'dni',
            'fecha_nacimiento', 'telefono', 'email', 'sexo',
            'estado_civil', 'direccion', 'latitud', 'longitud',
            'tipo_sangre', 'foto'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'sexo': forms.Select(choices=SexoChoices.choices),
            'estado_civil': forms.Select(choices=EstadoCivilChoices.choices),
            'latitud': forms.NumberInput(attrs={'step': '0.000001'}),
            'longitud': forms.NumberInput(attrs={'step': '0.000001'}),
            'direccion': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales
        self.fields['dni'].required = False
        self.fields['email'].required = False
        self.fields['latitud'].required = False
        self.fields['longitud'].required = False
        self.fields['foto'].required = False
        
        # Agregar clases de Tailwind CSS
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            })


class HistoriaClinicaForm(forms.ModelForm):
    """Formulario para actualizar la historia clínica de un paciente"""
    
    class Meta:
        model = Paciente
        fields = [
            'antecedentes_personales',
            'antecedentes_quirurgicos',
            'antecedentes_familiares',
            'alergias',
            'medicamentos_actuales',
            'habitos_toxicos',
            'vacunas',
            'antecedentes_gineco_obstetricos'
        ]
        widgets = {
            'antecedentes_personales': forms.Textarea(attrs={'rows': 4}),
            'antecedentes_quirurgicos': forms.Textarea(attrs={'rows': 4}),
            'antecedentes_familiares': forms.Textarea(attrs={'rows': 4}),
            'alergias': forms.Textarea(attrs={'rows': 3}),
            'medicamentos_actuales': forms.Textarea(attrs={'rows': 3}),
            'habitos_toxicos': forms.TextInput(),
            'vacunas': forms.Textarea(attrs={'rows': 3}),
            'antecedentes_gineco_obstetricos': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer todos los campos opcionales
        for field in self.fields:
            self.fields[field].required = False
            # Agregar clases de Tailwind CSS
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            })
