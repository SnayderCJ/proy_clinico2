import calendar
import json
from datetime import datetime, date, time, timedelta
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required

from applications.core.models import Paciente
from applications.doctor.models import CitaMedica, HorarioAtencion
from applications.doctor.utils.cita_medica import EstadoCitaChoices
from applications.doctor.utils.doctor import DiaSemanaChoices
from proy_clinico.util import save_audit

@login_required
def calendario_citas_mejorado(request):
    """Vista principal del calendario de citas con validaciones mejoradas"""
    # Obtener año y mes actual o de los parámetros
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    # Validar año y mes
    if year < 2020 or year > 2030:
        year = datetime.now().year
    if month < 1 or month > 12:
        month = datetime.now().month
    
    # Crear objeto de calendario
    cal = calendar.Calendar(firstweekday=0)  # Lunes como primer día
    month_days = cal.monthdayscalendar(year, month)
    
    # Obtener todas las citas del mes con información completa
    citas_mes = CitaMedica.objects.filter(
        fecha__year=year,
        fecha__month=month
    ).select_related('paciente').order_by('fecha', 'hora_cita')
    
    # Organizar citas por día con estadísticas
    citas_por_dia = {}
    estadisticas_mes = {
        'total_citas': 0,
        'pendientes': 0,
        'confirmadas': 0,
        'completadas': 0,
        'canceladas': 0,
        'ausentes': 0
    }
    
    for cita in citas_mes:
        dia = cita.fecha.day
        if dia not in citas_por_dia:
            citas_por_dia[dia] = []
        citas_por_dia[dia].append(cita)
        
        # Actualizar estadísticas
        estadisticas_mes['total_citas'] += 1
        if cita.estado == EstadoCitaChoices.PENDIENTE:
            estadisticas_mes['pendientes'] += 1
        elif cita.estado == EstadoCitaChoices.CONFIRMADA:
            estadisticas_mes['confirmadas'] += 1
        elif cita.estado == EstadoCitaChoices.COMPLETADA:
            estadisticas_mes['completadas'] += 1
        elif cita.estado == EstadoCitaChoices.CANCELADA:
            estadisticas_mes['canceladas'] += 1
        elif cita.estado == EstadoCitaChoices.AUSENTE:
            estadisticas_mes['ausentes'] += 1
    
    # Obtener horarios de atención activos
    horarios = HorarioAtencion.objects.filter(activo=True).order_by('dia_semana', 'hora_inicio')
    
    # Calcular mes anterior y siguiente
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Obtener días con horarios de atención
    dias_atencion = set()
    for horario in horarios:
        dias_atencion.add(horario.dia_semana)
    
    context = {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'month_days': month_days,
        'citas_por_dia': citas_por_dia,
        'horarios': horarios,
        'dias_atencion': dias_atencion,
        'estadisticas_mes': estadisticas_mes,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'estados_cita': EstadoCitaChoices.choices,
        'dias_semana': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
        'fecha_actual': date.today(),
        'hora_actual': timezone.now().time()
    }
    
    return render(request, 'doctor/calendario/calendario.html', context)

@login_required
def horarios_disponibles_mejorado(request):
    """API mejorada para obtener horarios disponibles con validaciones"""
    if request.method == 'GET':
        fecha_str = request.GET.get('fecha')
        if not fecha_str:
            return JsonResponse({'error': 'Fecha requerida'}, status=400)
        
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Formato de fecha inválido (YYYY-MM-DD)'}, status=400)
        
        # Validar que la fecha no sea en el pasado
        if fecha < date.today():
            return JsonResponse({
                'error': 'No se pueden agendar citas en fechas pasadas',
                'horarios_disponibles': []
            }, status=400)
        
        # Validar que la fecha no sea muy lejana (máximo 6 meses)
        fecha_limite = date.today() + timedelta(days=180)
        if fecha > fecha_limite:
            return JsonResponse({
                'error': 'No se pueden agendar citas con más de 6 meses de anticipación',
                'horarios_disponibles': []
            }, status=400)
        
        # Obtener día de la semana (0=lunes, 6=domingo)
        dia_semana_num = fecha.weekday()
        dias_semana_map = {
            0: DiaSemanaChoices.LUNES,
            1: DiaSemanaChoices.MARTES,
            2: DiaSemanaChoices.MIERCOLES,
            3: DiaSemanaChoices.JUEVES,
            4: DiaSemanaChoices.VIERNES,
            5: DiaSemanaChoices.SABADO,
            6: DiaSemanaChoices.DOMINGO,
        }
        
        dia_semana = dias_semana_map.get(dia_semana_num)
        
        # Obtener horarios de atención para ese día
        horarios = HorarioAtencion.objects.filter(
            dia_semana=dia_semana,
            activo=True
        ).order_by('hora_inicio')
        
        if not horarios.exists():
            return JsonResponse({
                'horarios_disponibles': [],
                'mensaje': f'No hay horarios de atención para {dia_semana}',
                'fecha': fecha_str
            })
        
        # Obtener citas ya agendadas para esa fecha (excluyendo canceladas)
        citas_ocupadas = CitaMedica.objects.filter(
            fecha=fecha
        ).exclude(
            estado=EstadoCitaChoices.CANCELADA
        ).values_list('hora_cita', flat=True)
        
        horarios_disponibles = []
        total_slots = 0
        slots_ocupados = 0
        
        for horario in horarios:
            # Generar slots de tiempo cada 30 minutos
            hora_actual = datetime.combine(fecha, horario.hora_inicio)
            hora_fin = datetime.combine(fecha, horario.hora_fin)
            
            while hora_actual < hora_fin:
                total_slots += 1
                
                # Verificar si está en el intervalo de pausa
                if (horario.intervalo_desde and horario.intervalo_hasta and
                    horario.intervalo_desde <= hora_actual.time() < horario.intervalo_hasta):
                    hora_actual += timedelta(minutes=30)
                    continue
                
                # Si es hoy, verificar que la hora no haya pasado
                if fecha == date.today():
                    hora_limite = timezone.now() + timedelta(hours=1)  # Mínimo 1 hora de anticipación
                    if hora_actual <= hora_limite:
                        horarios_disponibles.append({
                            'hora': hora_actual.strftime('%H:%M'),
                            'disponible': False,
                            'motivo': 'Hora ya pasada'
                        })
                        hora_actual += timedelta(minutes=30)
                        continue
                
                # Verificar si el horario no está ocupado
                if hora_actual.time() not in citas_ocupadas:
                    horarios_disponibles.append({
                        'hora': hora_actual.strftime('%H:%M'),
                        'disponible': True,
                        'motivo': 'Disponible'
                    })
                else:
                    slots_ocupados += 1
                    horarios_disponibles.append({
                        'hora': hora_actual.strftime('%H:%M'),
                        'disponible': False,
                        'motivo': 'Ocupado'
                    })
                
                hora_actual += timedelta(minutes=30)
        
        # Calcular estadísticas de disponibilidad
        slots_disponibles = len([h for h in horarios_disponibles if h['disponible']])
        porcentaje_ocupacion = (slots_ocupados / total_slots * 100) if total_slots > 0 else 0
        
        return JsonResponse({
            'horarios_disponibles': horarios_disponibles,
            'fecha': fecha_str,
            'dia_semana': dia_semana,
            'estadisticas': {
                'total_slots': total_slots,
                'slots_disponibles': slots_disponibles,
                'slots_ocupados': slots_ocupados,
                'porcentaje_ocupacion': round(porcentaje_ocupacion, 1)
            }
        })

@login_required
@csrf_exempt
def crear_cita_mejorada(request):
    """Vista mejorada para crear una nueva cita con validaciones completas"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar datos requeridos
            paciente_id = data.get('paciente_id')
            fecha_str = data.get('fecha')
            hora_str = data.get('hora')
            observaciones = data.get('observaciones', '').strip()
            
            if not all([paciente_id, fecha_str, hora_str]):
                return JsonResponse({
                    'success': False,
                    'error': 'Datos incompletos: paciente, fecha y hora son requeridos'
                }, status=400)
            
            with transaction.atomic():
                # Validar paciente
                try:
                    paciente = Paciente.objects.get(id=paciente_id, activo=True)
                except Paciente.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Paciente no encontrado o inactivo'
                    }, status=404)
                
                # Validar fecha y hora
                try:
                    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                    hora = datetime.strptime(hora_str, '%H:%M').time()
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Formato de fecha u hora inválido'
                    }, status=400)
                
                # Validaciones de negocio
                errores = validar_cita(fecha, hora, paciente)
                if errores:
                    return JsonResponse({
                        'success': False,
                        'error': '; '.join(errores)
                    }, status=400)
                
                # Verificar disponibilidad final
                cita_existente = CitaMedica.objects.filter(
                    fecha=fecha,
                    hora_cita=hora
                ).exclude(estado=EstadoCitaChoices.CANCELADA).exists()
                
                if cita_existente:
                    return JsonResponse({
                        'success': False,
                        'error': 'El horario seleccionado ya está ocupado'
                    }, status=400)
                
                # Verificar si el paciente ya tiene una cita el mismo día
                cita_mismo_dia = CitaMedica.objects.filter(
                    paciente=paciente,
                    fecha=fecha
                ).exclude(estado=EstadoCitaChoices.CANCELADA).exists()
                
                if cita_mismo_dia:
                    return JsonResponse({
                        'success': False,
                        'error': 'El paciente ya tiene una cita agendada para este día'
                    }, status=400)
                
                # Crear la cita
                cita = CitaMedica.objects.create(
                    paciente=paciente,
                    fecha=fecha,
                    hora_cita=hora,
                    estado=EstadoCitaChoices.PENDIENTE,
                    observaciones=observaciones
                )
                
                # Guardar auditoría
                save_audit(request, cita, "ADICION")
                
                return JsonResponse({
                    'success': True,
                    'cita_id': cita.id,
                    'mensaje': f'Cita creada exitosamente para {paciente.nombre_completo}',
                    'cita': {
                        'id': cita.id,
                        'paciente': paciente.nombre_completo,
                        'fecha': fecha.strftime('%Y-%m-%d'),
                        'hora': hora.strftime('%H:%M'),
                        'estado': cita.estado
                    }
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Datos JSON inválidos'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def validar_cita(fecha, hora, paciente):
    """Función para validar una cita médica"""
    errores = []
    
    # Validar que la fecha no sea en el pasado
    if fecha < date.today():
        errores.append('No se pueden agendar citas en fechas pasadas')
    
    # Validar que si es hoy, la hora no haya pasado
    if fecha == date.today():
        hora_limite = timezone.now() + timedelta(hours=1)
        if datetime.combine(fecha, hora) <= hora_limite:
            errores.append('Debe agendar con al menos 1 hora de anticipación')
    
    # Validar que la fecha no sea muy lejana
    fecha_limite = date.today() + timedelta(days=180)
    if fecha > fecha_limite:
        errores.append('No se pueden agendar citas con más de 6 meses de anticipación')
    
    # Validar que sea un día de atención
    dia_semana_num = fecha.weekday()
    dias_semana_map = {
        0: DiaSemanaChoices.LUNES,
        1: DiaSemanaChoices.MARTES,
        2: DiaSemanaChoices.MIERCOLES,
        3: DiaSemanaChoices.JUEVES,
        4: DiaSemanaChoices.VIERNES,
        5: DiaSemanaChoices.SABADO,
        6: DiaSemanaChoices.DOMINGO,
    }
    
    dia_semana = dias_semana_map.get(dia_semana_num)
    horarios_dia = HorarioAtencion.objects.filter(
        dia_semana=dia_semana,
        activo=True
    )
    
    if not horarios_dia.exists():
        errores.append(f'No hay atención médica los {dia_semana}')
    
    # Validar que la hora esté dentro de los horarios de atención
    hora_valida = False
    for horario in horarios_dia:
        if horario.hora_inicio <= hora <= horario.hora_fin:
            # Verificar que no esté en pausa
            if (horario.intervalo_desde and horario.intervalo_hasta and
                horario.intervalo_desde <= hora < horario.intervalo_hasta):
                errores.append('La hora seleccionada está en horario de pausa')
            else:
                hora_valida = True
                break
    
    if not hora_valida and not any('pausa' in error for error in errores):
        errores.append('La hora seleccionada está fuera del horario de atención')
    
    # Validar que la hora sea en intervalos de 30 minutos
    if hora.minute not in [0, 30]:
        errores.append('Las citas solo se pueden agendar cada 30 minutos (ej: 09:00, 09:30)')
    
    return errores

@login_required
@csrf_exempt
def editar_cita_mejorada(request, cita_id):
    """Vista mejorada para editar una cita existente"""
    cita = get_object_or_404(CitaMedica, id=cita_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            with transaction.atomic():
                cambios = []
                
                # Actualizar estado
                if 'estado' in data and data['estado'] != cita.estado:
                    estado_anterior = cita.estado
                    cita.estado = data['estado']
                    cambios.append(f'Estado: {estado_anterior} → {cita.estado}')
                
                # Actualizar observaciones
                if 'observaciones' in data:
                    cita.observaciones = data['observaciones'].strip()
                    cambios.append('Observaciones actualizadas')
                
                # Actualizar fecha y hora si se proporcionan
                if 'fecha' in data and 'hora' in data:
                    try:
                        nueva_fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
                        nueva_hora = datetime.strptime(data['hora'], '%H:%M').time()
                        
                        # Verificar si cambió la fecha/hora
                        if nueva_fecha != cita.fecha or nueva_hora != cita.hora_cita:
                            # Validar nueva fecha/hora
                            errores = validar_cita(nueva_fecha, nueva_hora, cita.paciente)
                            if errores:
                                return JsonResponse({
                                    'success': False,
                                    'error': '; '.join(errores)
                                }, status=400)
                            
                            # Verificar disponibilidad
                            cita_existente = CitaMedica.objects.filter(
                                fecha=nueva_fecha,
                                hora_cita=nueva_hora
                            ).exclude(
                                id=cita.id
                            ).exclude(
                                estado=EstadoCitaChoices.CANCELADA
                            ).exists()
                            
                            if cita_existente:
                                return JsonResponse({
                                    'success': False,
                                    'error': 'El nuevo horario ya está ocupado'
                                }, status=400)
                            
                            cambios.append(f'Fecha: {cita.fecha} → {nueva_fecha}')
                            cambios.append(f'Hora: {cita.hora_cita} → {nueva_hora}')
                            cita.fecha = nueva_fecha
                            cita.hora_cita = nueva_hora
                    
                    except ValueError:
                        return JsonResponse({
                            'success': False,
                            'error': 'Formato de fecha u hora inválido'
                        }, status=400)
                
                cita.save()
                
                # Guardar auditoría
                save_audit(request, cita, "MODIFICACION")
                
                return JsonResponse({
                    'success': True,
                    'mensaje': f'Cita actualizada exitosamente. Cambios: {", ".join(cambios)}' if cambios else 'Cita actualizada',
                    'cambios': cambios
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Datos JSON inválidos'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)
    
    # GET request - devolver datos de la cita
    return JsonResponse({
        'cita': {
            'id': cita.id,
            'paciente_id': cita.paciente.id,
            'paciente_nombre': cita.paciente.nombre_completo,
            'paciente_cedula': cita.paciente.cedula_ecuatoriana,
            'paciente_telefono': cita.paciente.telefono,
            'fecha': cita.fecha.strftime('%Y-%m-%d'),
            'hora': cita.hora_cita.strftime('%H:%M'),
            'estado': cita.estado,
            'estado_display': cita.get_estado_display(),
            'observaciones': cita.observaciones or '',
            'puede_editar': cita.fecha >= date.today(),
            'puede_cancelar': cita.estado not in [EstadoCitaChoices.COMPLETADA, EstadoCitaChoices.CANCELADA]
        }
    })

@login_required
@csrf_exempt
def eliminar_cita_mejorada(request, cita_id):
    """Vista mejorada para eliminar/cancelar una cita"""
    if request.method == 'DELETE':
        try:
            cita = get_object_or_404(CitaMedica, id=cita_id)
            
            # Verificar si se puede cancelar
            if cita.estado in [EstadoCitaChoices.COMPLETADA]:
                return JsonResponse({
                    'success': False,
                    'error': 'No se puede cancelar una cita que ya fue completada'
                }, status=400)
            
            if cita.estado == EstadoCitaChoices.CANCELADA:
                return JsonResponse({
                    'success': False,
                    'error': 'La cita ya está cancelada'
                }, status=400)
            
            # Verificar si es el mismo día (requiere confirmación especial)
            if cita.fecha == date.today():
                motivo = request.GET.get('motivo', '')
                if not motivo:
                    return JsonResponse({
                        'success': False,
                        'error': 'Se requiere un motivo para cancelar citas el mismo día'
                    }, status=400)
                cita.observaciones = f"CANCELADA EL MISMO DÍA: {motivo}. {cita.observaciones or ''}"
            
            estado_anterior = cita.estado
            cita.estado = EstadoCitaChoices.CANCELADA
            cita.save()
            
            # Guardar auditoría
            save_audit(request, cita, "CANCELACION")
            
            return JsonResponse({
                'success': True,
                'mensaje': f'Cita cancelada exitosamente (era {estado_anterior})'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def buscar_pacientes_mejorado(request):
    """API mejorada para buscar pacientes con más información"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({
            'pacientes': [],
            'mensaje': 'Ingrese al menos 2 caracteres para buscar'
        })
    
    # Buscar por nombre, apellido o cédula
    pacientes = Paciente.objects.filter(
        Q(nombres__icontains=query) |
        Q(apellidos__icontains=query) |
        Q(cedula_ecuatoriana__icontains=query),
        activo=True
    ).order_by('apellidos', 'nombres')[:15]  # Limitar a 15 resultados
    
    pacientes_data = []
    for paciente in pacientes:
        # Obtener última cita
        ultima_cita = CitaMedica.objects.filter(
            paciente=paciente
        ).order_by('-fecha', '-hora_cita').first()
        
        pacientes_data.append({
            'id': paciente.id,
            'nombre_completo': paciente.nombre_completo,
            'cedula': paciente.cedula_ecuatoriana,
            'telefono': paciente.telefono,
            'email': paciente.email or '',
            'edad': paciente.edad,
            'ultima_cita': ultima_cita.fecha.strftime('%Y-%m-%d') if ultima_cita else 'Sin citas',
            'total_citas': CitaMedica.objects.filter(paciente=paciente).count()
        })
    
    return JsonResponse({
        'pacientes': pacientes_data,
        'total_encontrados': len(pacientes_data),
        'query': query
    })

@login_required
def estadisticas_calendario(request):
    """API para obtener estadísticas del calendario"""
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    # Obtener citas del mes
    citas_mes = CitaMedica.objects.filter(
        fecha__year=year,
        fecha__month=month
    )
    
    # Calcular estadísticas
    estadisticas = {
        'total_citas': citas_mes.count(),
        'por_estado': {},
        'por_dia': {},
        'horarios_mas_solicitados': {},
        'pacientes_frecuentes': []
    }
    
    # Estadísticas por estado
    for estado, _ in EstadoCitaChoices.choices:
        estadisticas['por_estado'][estado] = citas_mes.filter(estado=estado).count()
    
    # Estadísticas por día
    for cita in citas_mes:
        dia = cita.fecha.day
        if dia not in estadisticas['por_dia']:
            estadisticas['por_dia'][dia] = 0
        estadisticas['por_dia'][dia] += 1
    
    # Horarios más solicitados
    horarios = citas_mes.values('hora_cita').annotate(
        total=models.Count('hora_cita')
    ).order_by('-total')[:5]
    
    for horario in horarios:
        hora_str = horario['hora_cita'].strftime('%H:%M')
        estadisticas['horarios_mas_solicitados'][hora_str] = horario['total']
    
    return JsonResponse(estadisticas)
