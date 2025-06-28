# Importar las funciones mejoradas para mantener compatibilidad
from .calendario_mejorado import (
    calendario_citas_mejorado as calendario_citas,
    horarios_disponibles_mejorado as horarios_disponibles,
    crear_cita_mejorada as crear_cita,
    editar_cita_mejorada as editar_cita,
    eliminar_cita_mejorada as eliminar_cita,
    buscar_pacientes_mejorado as buscar_pacientes,
    estadisticas_calendario
)

# Re-exportar todas las funciones para mantener compatibilidad
__all__ = [
    'calendario_citas',
    'horarios_disponibles', 
    'crear_cita',
    'editar_cita',
    'eliminar_cita',
    'buscar_pacientes',
    'estadisticas_calendario'
]
  