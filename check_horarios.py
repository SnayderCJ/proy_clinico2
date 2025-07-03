import os
import django
import sys

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proy_clinico.settings')
django.setup()

from applications.doctor.models import HorarioAtencion
from applications.core.models import Doctor

print("=== DIAGNÓSTICO DE HORARIOS ===")

# Verificar doctores
doctores = Doctor.objects.all()
print(f"Doctores registrados: {doctores.count()}")

# Verificar horarios
horarios = HorarioAtencion.objects.all()
print(f"Horarios totales: {horarios.count()}")

horarios_activos = HorarioAtencion.objects.filter(activo=True)
print(f"Horarios activos: {horarios_activos.count()}")

if horarios_activos.count() == 0:
    print("\n❌ PROBLEMA: No hay horarios activos configurados")
    print("SOLUCIÓN: Configura horarios en /doctor/horarios/crear/")
else:
    print("\n✅ Horarios activos encontrados:")
    for h in horarios_activos:
        print(f"  - {h.get_dia_semana_display()}: {h.hora_inicio} - {h.hora_fin}")
