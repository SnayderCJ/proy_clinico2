from django import forms
from django.forms import formset_factory
from applications.doctor.models import HorarioAtencion
from applications.doctor.utils.doctor import DiaSemanaChoices


class HorarioAtencionForm(forms.ModelForm):
    """Formulario para un horario individual"""
    
    class Meta:
        model = HorarioAtencion
        fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'intervalo_desde', 'intervalo_hasta', 'activo']
        widgets = {
            'dia_semana': forms.Select(attrs={
                'class': 'form-select',
                'readonly': True
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'intervalo_desde': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'intervalo_hasta': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        intervalo_desde = cleaned_data.get('intervalo_desde')
        intervalo_hasta = cleaned_data.get('intervalo_hasta')

        # Validar que hora_fin sea mayor que hora_inicio
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise forms.ValidationError("La hora de fin debe ser posterior a la hora de inicio.")

        # Validar intervalos de descanso
        if intervalo_desde and intervalo_hasta:
            if intervalo_desde >= intervalo_hasta:
                raise forms.ValidationError("El intervalo de descanso debe tener una hora de fin posterior al inicio.")
            
            if hora_inicio and hora_fin:
                if not (hora_inicio <= intervalo_desde < intervalo_hasta <= hora_fin):
                    raise forms.ValidationError("El intervalo de descanso debe estar dentro del horario de atención.")

        return cleaned_data


class HorarioSemanalForm(forms.Form):
    """Formulario para gestionar todos los horarios de la semana"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Crear campos para cada día de la semana
        for dia_choice in DiaSemanaChoices.choices:
            dia_key = dia_choice[0]
            dia_label = dia_choice[1]
            
            # Campo activo
            self.fields[f'{dia_key}_activo'] = forms.BooleanField(
                required=False,
                label=f'{dia_label} - Activo',
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
            )
            
            # Hora inicio
            self.fields[f'{dia_key}_hora_inicio'] = forms.TimeField(
                required=False,
                label='Hora Inicio',
                widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
            )
            
            # Hora fin
            self.fields[f'{dia_key}_hora_fin'] = forms.TimeField(
                required=False,
                label='Hora Fin',
                widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
            )
            
            # Intervalo desde
            self.fields[f'{dia_key}_intervalo_desde'] = forms.TimeField(
                required=False,
                label='Descanso Desde',
                widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
            )
            
            # Intervalo hasta
            self.fields[f'{dia_key}_intervalo_hasta'] = forms.TimeField(
                required=False,
                label='Descanso Hasta',
                widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
            )

    def clean(self):
        cleaned_data = super().clean()
        
        for dia_choice in DiaSemanaChoices.choices:
            dia_key = dia_choice[0]
            
            activo = cleaned_data.get(f'{dia_key}_activo')
            hora_inicio = cleaned_data.get(f'{dia_key}_hora_inicio')
            hora_fin = cleaned_data.get(f'{dia_key}_hora_fin')
            intervalo_desde = cleaned_data.get(f'{dia_key}_intervalo_desde')
            intervalo_hasta = cleaned_data.get(f'{dia_key}_intervalo_hasta')
            
            # Si está activo, validar campos obligatorios
            if activo:
                if not hora_inicio:
                    raise forms.ValidationError(f"Debe especificar hora de inicio para {dia_choice[1]}")
                if not hora_fin:
                    raise forms.ValidationError(f"Debe especificar hora de fin para {dia_choice[1]}")
                
                # Validar que hora_fin sea mayor que hora_inicio
                if hora_inicio >= hora_fin:
                    raise forms.ValidationError(f"La hora de fin debe ser posterior a la hora de inicio para {dia_choice[1]}")
                
                # Validar intervalos de descanso
                if intervalo_desde and intervalo_hasta:
                    if intervalo_desde >= intervalo_hasta:
                        raise forms.ValidationError(f"El intervalo de descanso debe tener una hora de fin posterior al inicio para {dia_choice[1]}")
                    
                    if not (hora_inicio <= intervalo_desde < intervalo_hasta <= hora_fin):
                        raise forms.ValidationError(f"El intervalo de descanso debe estar dentro del horario de atención para {dia_choice[1]}")
        
        return cleaned_data

    def save(self, doctor=None):
        """Guarda todos los horarios de la semana usando generación automática"""
        from applications.core.models import Doctor
        
        # Si no se proporciona doctor, usar el primero disponible
        if not doctor:
            doctor = Doctor.objects.first()
            if not doctor:
                raise ValueError("No hay doctores registrados en el sistema")
        
        # Preparar datos para la generación automática
        horarios_data = []
        
        for dia_choice in DiaSemanaChoices.choices:
            dia_key = dia_choice[0]
            
            activo = self.cleaned_data.get(f'{dia_key}_activo', False)
            
            if activo:
                hora_inicio = self.cleaned_data.get(f'{dia_key}_hora_inicio')
                hora_fin = self.cleaned_data.get(f'{dia_key}_hora_fin')
                intervalo_desde = self.cleaned_data.get(f'{dia_key}_intervalo_desde')
                intervalo_hasta = self.cleaned_data.get(f'{dia_key}_intervalo_hasta')
                
                if hora_inicio and hora_fin:
                    horarios_data.append({
                        'dia_semana': dia_key,
                        'hora_inicio': hora_inicio,
                        'hora_fin': hora_fin,
                        'intervalo_desde': intervalo_desde,
                        'intervalo_hasta': intervalo_hasta,
                        'activo': activo
                    })
        
        # Usar el método de generación automática del modelo
        horarios_creados = HorarioAtencion.generar_horarios_automaticos(doctor, horarios_data)
        
        return horarios_creados

    def load_existing_data(self):
        """Carga datos existentes en el formulario"""
        horarios_existentes = HorarioAtencion.objects.filter(activo=True)
        
        initial_data = {}
        for horario in horarios_existentes:
            dia_key = horario.dia_semana
            initial_data[f'{dia_key}_activo'] = horario.activo
            initial_data[f'{dia_key}_hora_inicio'] = horario.hora_inicio
            initial_data[f'{dia_key}_hora_fin'] = horario.hora_fin
            initial_data[f'{dia_key}_intervalo_desde'] = horario.intervalo_desde
            initial_data[f'{dia_key}_intervalo_hasta'] = horario.intervalo_hasta
        
        return initial_data
