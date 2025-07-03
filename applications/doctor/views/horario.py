from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from applications.doctor.models import HorarioAtencion
from applications.doctor.forms.horario import HorarioSemanalForm
from applications.doctor.utils.doctor import DiaSemanaChoices
from applications.core.models import Doctor


@method_decorator(login_required, name='dispatch')
class HorarioListView(ListView):
    """Vista para listar todos los horarios de atención"""
    model = HorarioAtencion
    template_name = 'doctor/horarios/list.html'
    context_object_name = 'horarios'

    def get_queryset(self):
        return HorarioAtencion.objects.all().order_by('dia_semana', 'hora_inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dias_semana'] = DiaSemanaChoices.choices
        
        # Obtener información del doctor para el modal
        try:
            doctor = Doctor.objects.prefetch_related('especialidad').first()
            context['doctor'] = doctor
            # Obtener todas las especialidades del doctor
            context['especialidades'] = doctor.especialidad.all() if doctor else []
        except Doctor.DoesNotExist:
            context['doctor'] = None
            context['especialidades'] = []
        
        return context


@login_required
def horario_semanal_create_view(request):
    """Vista para crear/actualizar horarios semanales"""
    if request.method == 'POST':
        form = HorarioSemanalForm(request.POST)
        if form.is_valid():
            try:
                horarios_creados = form.save()
                messages.success(
                    request, 
                    f'Horarios semanales guardados exitosamente. Se crearon {len(horarios_creados)} horarios.'
                )
                return redirect('doctor:horario_list')
            except Exception as e:
                messages.error(request, f'Error al guardar los horarios: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = HorarioSemanalForm()
        # Cargar datos existentes
        initial_data = form.load_existing_data()
        form = HorarioSemanalForm(initial=initial_data)
    
    context = {
        'form': form,
        'dias_semana': DiaSemanaChoices.choices,
        'title': 'Gestión de Horarios Semanales'
    }
    return render(request, 'doctor/horarios/form.html', context)


@method_decorator(login_required, name='dispatch')
class HorarioDetailView(DetailView):
    """Vista para mostrar detalles de un horario específico"""
    model = HorarioAtencion
    template_name = 'doctor/horarios/detail.html'
    context_object_name = 'horario'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        horario = self.get_object()
        
        # Obtener información del doctor
        try:
            doctor = Doctor.objects.prefetch_related('especialidad').first()
            context['doctor'] = doctor
            # Obtener todas las especialidades del doctor
            context['especialidades'] = doctor.especialidad.all() if doctor else []
        except Doctor.DoesNotExist:
            context['doctor'] = None
            context['especialidades'] = []
        
        # Calcular duración total del horario
        if horario.hora_inicio and horario.hora_fin:
            from datetime import datetime
            inicio = datetime.combine(datetime.today(), horario.hora_inicio)
            fin = datetime.combine(datetime.today(), horario.hora_fin)
            duracion_total = fin - inicio
            
            # Restar tiempo de descanso si existe
            if horario.intervalo_desde and horario.intervalo_hasta:
                descanso_inicio = datetime.combine(datetime.today(), horario.intervalo_desde)
                descanso_fin = datetime.combine(datetime.today(), horario.intervalo_hasta)
                duracion_descanso = descanso_fin - descanso_inicio
                duracion_total -= duracion_descanso
            
            context['duracion_horas'] = duracion_total.total_seconds() / 3600
        
        return context


@login_required
def horario_info_doctor(request, pk):
    """Vista AJAX para obtener información del doctor y horario"""
    horario = get_object_or_404(HorarioAtencion, pk=pk)
    
    try:
        doctor = Doctor.objects.first()
        doctor_info = {
            'nombre': doctor.nombre_completo if doctor else 'No disponible',
            'especialidad': str(doctor.especialidad) if doctor and doctor.especialidad else 'No especificada',
            'duracion_atencion': doctor.duracion_atencion if doctor else 30,
            'telefono': doctor.telefonos if doctor else 'No disponible',
            'email': doctor.email if doctor else 'No disponible'
        }
    except (Doctor.DoesNotExist, AttributeError):
        doctor_info = {
            'nombre': 'No disponible',
            'especialidad': 'No especificada',
            'duracion_atencion': 30,
            'telefono': 'No disponible',
            'email': 'No disponible'
        }
    
    # Calcular duración del horario
    if horario.hora_inicio and horario.hora_fin:
        from datetime import datetime
        inicio = datetime.combine(datetime.today(), horario.hora_inicio)
        fin = datetime.combine(datetime.today(), horario.hora_fin)
        duracion_total = fin - inicio
        
        # Restar tiempo de descanso
        if horario.intervalo_desde and horario.intervalo_hasta:
            descanso_inicio = datetime.combine(datetime.today(), horario.intervalo_desde)
            descanso_fin = datetime.combine(datetime.today(), horario.intervalo_hasta)
            duracion_descanso = descanso_fin - descanso_inicio
            duracion_total -= duracion_descanso
        
        duracion_horas = duracion_total.total_seconds() / 3600
    else:
        duracion_horas = 0
    
    horario_info = {
        'dia_semana': horario.get_dia_semana_display(),
        'hora_inicio': horario.hora_inicio.strftime('%H:%M') if horario.hora_inicio else '',
        'hora_fin': horario.hora_fin.strftime('%H:%M') if horario.hora_fin else '',
        'intervalo_desde': horario.intervalo_desde.strftime('%H:%M') if horario.intervalo_desde else '',
        'intervalo_hasta': horario.intervalo_hasta.strftime('%H:%M') if horario.intervalo_hasta else '',
        'duracion_horas': round(duracion_horas, 2),
        'activo': horario.activo
    }
    
    return JsonResponse({
        'success': True,
        'doctor': doctor_info,
        'horario': horario_info
    })
