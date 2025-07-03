#!/usr/bin/env python
"""
Script para verificar la configuración de horarios de atención
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proy_clinico.settings')
django.setup()

from applications.doctor.models import HorarioAtencion
from applications.core.models import Doctor

def verificar_horarios():
    print("=== VERIFICACIÓN DE HORARIOS DE ATENCIÓN ===\n")
    
    # Verificar si hay doctores
    doctores = Doctor.objects.all()
    print(f"📋 Total de doctores en el sistema: {doctores.count()}")
    
    if doctores.count() == 0:
        print("❌ No hay doctores registrados en el sistema")
        return
    
    for doctor in doctores:
        print(f"\n👨‍⚕️ Doctor: {doctor.nombre_completo}")
        print(f"   Especialidades: {', '.join([str(esp) for esp in doctor.especialidad.all()])}")
        print(f"   Duración de atención: {doctor.duracion_atencion} minutos")
    
    # Verificar horarios de atención
    horarios = HorarioAtencion.objects.all()
    print(f"\n📅 Total de horarios configurados: {horarios.count()}")
    
    if horarios.count() == 0:
        print("❌ NO HAY HORARIOS DE ATENCIÓN CONFIGURADOS")
        print("   Esto explica por qué no aparecen horarios disponibles para las citas.")
        print("\n💡 SOLUCIÓN:")
        print("   1. Ve al módulo de 'Horarios de Atención'")
        print("   2. Configura los horarios para cada día de la semana")
        print("   3. Asegúrate de marcar los horarios como 'activo'")
        return
    
    # Mostrar horarios configurados
    print("\n📋 Horarios configurados:")
    horarios_activos = 0
    
    for horario in horarios.order_by('dia_semana', 'hora_inicio'):
        estado = "✅ ACTIVO" if horario.activo else "❌ INACTIVO"
        print(f"   {horario.get_dia_semana_display()}: {horario.hora_inicio} - {horario.hora_fin} {estado}")
        
        if horario.intervalo_desde and horario.intervalo_hasta:
            print(f"      Pausa: {horario.intervalo_desde} - {horario.intervalo_hasta}")
        
        if horario.activo:
            horarios_activos += 1
    
    print(f"\n📊 Resumen:")
    print(f"   - Horarios totales: {horarios.count()}")
    print(f"   - Horarios activos: {horarios_activos}")
    print(f"   - Horarios inactivos: {horarios.count() - horarios_activos}")
    
    if horarios_activos == 0:
        print("\n❌ PROBLEMA ENCONTRADO:")
        print("   Hay horarios configurados pero NINGUNO está activo.")
        print("   Activa al menos un horario para que aparezcan citas disponibles.")
    else:
        print(f"\n✅ Configuración correcta: {horarios_activos} horarios activos")

if __name__ == "__main__":
    verificar_horarios()
