from django.urls import path
from applications.doctor.views import calendario_mejorado
from applications.doctor.views.atencion_medica import (
    AtencionListView, AtencionCreateView, AtencionUpdateView, AtencionDeleteView
)

app_name = 'doctor'

urlpatterns = [
    # Calendario de citas mejorado
    path('calendario/', calendario_mejorado.calendario_citas_mejorado, name='calendario_citas'),
    path('api/horarios-disponibles/', calendario_mejorado.horarios_disponibles_mejorado, name='horarios_disponibles'),
    path('api/crear-cita/', calendario_mejorado.crear_cita_mejorada, name='crear_cita'),
    path('api/editar-cita/<int:cita_id>/', calendario_mejorado.editar_cita_mejorada, name='editar_cita'),
    path('api/eliminar-cita/<int:cita_id>/', calendario_mejorado.eliminar_cita_mejorada, name='eliminar_cita'),
    path('api/buscar-pacientes/', calendario_mejorado.buscar_pacientes_mejorado, name='buscar_pacientes'),
    path('api/estadisticas/', calendario_mejorado.estadisticas_calendario, name='estadisticas_calendario'),
    
    # Atenciones médicas
    path('atenciones/', AtencionListView.as_view(), name='atencion_list'),
    path('atenciones/crear/', AtencionCreateView.as_view(), name='atencion_create'),
    path('atenciones/editar/<int:pk>/', AtencionUpdateView.as_view(), name='atencion_update'),
    path('atenciones/eliminar/<int:pk>/', AtencionDeleteView.as_view(), name='atencion_delete'),
]
