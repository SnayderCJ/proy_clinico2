from django.urls import path
from applications.core.views.paciente import (
    paciente_find, PacienteListView, PacienteCreateView, 
    PacienteUpdateView, PacienteDeleteView, PacienteDetailView,
    paciente_historia_clinica, paciente_fotos
)

app_name='core' # define un espacio de nombre para la aplicacion
urlpatterns = [
    # Rutas para vistas relacionadas con Pacientes
    path('pacientes/', PacienteListView.as_view(), name="paciente_list"),
    path('pacientes/crear/', PacienteCreateView.as_view(), name="paciente_create"),
    path('pacientes/<int:pk>/', PacienteDetailView.as_view(), name="paciente_detail"),
    path('pacientes/<int:pk>/editar/', PacienteUpdateView.as_view(), name="paciente_update"),
    path('pacientes/<int:pk>/eliminar/', PacienteDeleteView.as_view(), name="paciente_delete"),
    path('pacientes/<int:pk>/historia/', paciente_historia_clinica, name="paciente_historia"),
    path('pacientes/<int:pk>/fotos/', paciente_fotos, name="paciente_fotos"),
    
    # API para búsqueda
    path('paciente_find/', paciente_find, name="paciente_find"),
]
