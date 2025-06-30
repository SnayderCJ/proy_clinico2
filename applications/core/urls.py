from django.urls import path
from applications.core.views.paciente import (
    paciente_find, PacienteListView, PacienteCreateView, 
    PacienteUpdateView, PacienteDeleteView, PacienteDetailView,
    paciente_historia_clinica, paciente_fotos
)
from applications.core.views.tipo_sangre import (
    TipoSangreListView, TipoSangreCreateView, TipoSangreUpdateView, TipoSangreDeleteView
)
from applications.core.views.especialidad import (
    EspecialidadListView, EspecialidadCreateView, EspecialidadUpdateView, EspecialidadDeleteView
)
from applications.core.views.doctor import (
    DoctorListView, DoctorCreateView, DoctorUpdateView, DoctorDeleteView, DoctorDetailView
)
from applications.core.views.cargo import (
    CargoListView, CargoCreateView, CargoUpdateView, CargoDeleteView
)
from applications.core.views.empleado import (
    EmpleadoListView, EmpleadoCreateView, EmpleadoUpdateView, EmpleadoDeleteView, EmpleadoDetailView
)
from applications.core.views.medicamento import (
    TipoMedicamentoListView, TipoMedicamentoCreateView, TipoMedicamentoUpdateView, TipoMedicamentoDeleteView,
    MarcaMedicamentoListView, MarcaMedicamentoCreateView, MarcaMedicamentoUpdateView, MarcaMedicamentoDeleteView,
    MedicamentoListView, MedicamentoCreateView, MedicamentoUpdateView, MedicamentoDeleteView, MedicamentoDetailView
)
from applications.core.views.diagnostico import (
    DiagnosticoListView, DiagnosticoCreateView, DiagnosticoUpdateView, DiagnosticoDeleteView
)
from applications.core.views.gasto import (
    TipoGastoListView, TipoGastoCreateView, TipoGastoUpdateView, TipoGastoDeleteView,
    GastoMensualListView, GastoMensualCreateView, GastoMensualUpdateView, GastoMensualDeleteView
)
from applications.core.views.foto_paciente import (
    FotoPacienteListView, FotoPacienteCreateView, FotoPacienteUpdateView, FotoPacienteDeleteView,
    fotos_por_paciente
)

app_name='core' # define un espacio de nombre para la aplicacion
urlpatterns = [
    # ============================================================================
    # RUTAS PARA PACIENTES
    # ============================================================================
    path('pacientes/', PacienteListView.as_view(), name="paciente_list"),
    path('pacientes/crear/', PacienteCreateView.as_view(), name="paciente_create"),
    path('pacientes/<int:pk>/', PacienteDetailView.as_view(), name="paciente_detail"),
    path('pacientes/<int:pk>/editar/', PacienteUpdateView.as_view(), name="paciente_update"),
    path('pacientes/<int:pk>/eliminar/', PacienteDeleteView.as_view(), name="paciente_delete"),
    path('pacientes/<int:pk>/historia/', paciente_historia_clinica, name="paciente_historia"),
    path('pacientes/<int:pk>/fotos/', paciente_fotos, name="paciente_fotos"),
    
    # ============================================================================
    # RUTAS PARA TIPOS DE SANGRE
    # ============================================================================
    path('tipos-sangre/', TipoSangreListView.as_view(), name="tipo_sangre_list"),
    path('tipos-sangre/crear/', TipoSangreCreateView.as_view(), name="tipo_sangre_create"),
    path('tipos-sangre/<int:pk>/editar/', TipoSangreUpdateView.as_view(), name="tipo_sangre_update"),
    path('tipos-sangre/<int:pk>/eliminar/', TipoSangreDeleteView.as_view(), name="tipo_sangre_delete"),
    
    # ============================================================================
    # RUTAS PARA ESPECIALIDADES
    # ============================================================================
    path('especialidades/', EspecialidadListView.as_view(), name="especialidad_list"),
    path('especialidades/crear/', EspecialidadCreateView.as_view(), name="especialidad_create"),
    path('especialidades/<int:pk>/editar/', EspecialidadUpdateView.as_view(), name="especialidad_update"),
    path('especialidades/<int:pk>/eliminar/', EspecialidadDeleteView.as_view(), name="especialidad_delete"),
    
    # ============================================================================
    # RUTAS PARA DOCTORES
    # ============================================================================
    path('doctores/', DoctorListView.as_view(), name="doctor_list"),
    path('doctores/crear/', DoctorCreateView.as_view(), name="doctor_create"),
    path('doctores/<int:pk>/', DoctorDetailView.as_view(), name="doctor_detail"),
    path('doctores/<int:pk>/editar/', DoctorUpdateView.as_view(), name="doctor_update"),
    path('doctores/<int:pk>/eliminar/', DoctorDeleteView.as_view(), name="doctor_delete"),
    
    # ============================================================================
    # RUTAS PARA CARGOS
    # ============================================================================
    path('cargos/', CargoListView.as_view(), name="cargo_list"),
    path('cargos/crear/', CargoCreateView.as_view(), name="cargo_create"),
    path('cargos/<int:pk>/editar/', CargoUpdateView.as_view(), name="cargo_update"),
    path('cargos/<int:pk>/eliminar/', CargoDeleteView.as_view(), name="cargo_delete"),
    
    # ============================================================================
    # RUTAS PARA EMPLEADOS
    # ============================================================================
    path('empleados/', EmpleadoListView.as_view(), name="empleado_list"),
    path('empleados/crear/', EmpleadoCreateView.as_view(), name="empleado_create"),
    path('empleados/<int:pk>/', EmpleadoDetailView.as_view(), name="empleado_detail"),
    path('empleados/<int:pk>/editar/', EmpleadoUpdateView.as_view(), name="empleado_update"),
    path('empleados/<int:pk>/eliminar/', EmpleadoDeleteView.as_view(), name="empleado_delete"),
    
    # ============================================================================
    # RUTAS PARA TIPOS DE MEDICAMENTOS
    # ============================================================================
    path('tipos-medicamento/', TipoMedicamentoListView.as_view(), name="tipo_medicamento_list"),
    path('tipos-medicamento/crear/', TipoMedicamentoCreateView.as_view(), name="tipo_medicamento_create"),
    path('tipos-medicamento/<int:pk>/editar/', TipoMedicamentoUpdateView.as_view(), name="tipo_medicamento_update"),
    path('tipos-medicamento/<int:pk>/eliminar/', TipoMedicamentoDeleteView.as_view(), name="tipo_medicamento_delete"),
    
    # ============================================================================
    # RUTAS PARA MARCAS DE MEDICAMENTOS
    # ============================================================================
    path('marcas-medicamento/', MarcaMedicamentoListView.as_view(), name="marca_medicamento_list"),
    path('marcas-medicamento/crear/', MarcaMedicamentoCreateView.as_view(), name="marca_medicamento_create"),
    path('marcas-medicamento/<int:pk>/editar/', MarcaMedicamentoUpdateView.as_view(), name="marca_medicamento_update"),
    path('marcas-medicamento/<int:pk>/eliminar/', MarcaMedicamentoDeleteView.as_view(), name="marca_medicamento_delete"),
    
    # ============================================================================
    # RUTAS PARA MEDICAMENTOS
    # ============================================================================
    path('medicamentos/', MedicamentoListView.as_view(), name="medicamento_list"),
    path('medicamentos/crear/', MedicamentoCreateView.as_view(), name="medicamento_create"),
    path('medicamentos/<int:pk>/', MedicamentoDetailView.as_view(), name="medicamento_detail"),
    path('medicamentos/<int:pk>/editar/', MedicamentoUpdateView.as_view(), name="medicamento_update"),
    path('medicamentos/<int:pk>/eliminar/', MedicamentoDeleteView.as_view(), name="medicamento_delete"),
    
    # ============================================================================
    # RUTAS PARA DIAGNÓSTICOS
    # ============================================================================
    path('diagnosticos/', DiagnosticoListView.as_view(), name="diagnostico_list"),
    path('diagnosticos/crear/', DiagnosticoCreateView.as_view(), name="diagnostico_create"),
    path('diagnosticos/<int:pk>/editar/', DiagnosticoUpdateView.as_view(), name="diagnostico_update"),
    path('diagnosticos/<int:pk>/eliminar/', DiagnosticoDeleteView.as_view(), name="diagnostico_delete"),
    
    # ============================================================================
    # RUTAS PARA TIPOS DE GASTOS
    # ============================================================================
    path('tipos-gasto/', TipoGastoListView.as_view(), name="tipo_gasto_list"),
    path('tipos-gasto/crear/', TipoGastoCreateView.as_view(), name="tipo_gasto_create"),
    path('tipos-gasto/<int:pk>/editar/', TipoGastoUpdateView.as_view(), name="tipo_gasto_update"),
    path('tipos-gasto/<int:pk>/eliminar/', TipoGastoDeleteView.as_view(), name="tipo_gasto_delete"),
    
    # ============================================================================
    # RUTAS PARA GASTOS MENSUALES
    # ============================================================================
    path('gastos-mensuales/', GastoMensualListView.as_view(), name="gasto_mensual_list"),
    path('gastos-mensuales/crear/', GastoMensualCreateView.as_view(), name="gasto_mensual_create"),
    path('gastos-mensuales/<int:pk>/editar/', GastoMensualUpdateView.as_view(), name="gasto_mensual_update"),
    path('gastos-mensuales/<int:pk>/eliminar/', GastoMensualDeleteView.as_view(), name="gasto_mensual_delete"),
    
    # ============================================================================
    # RUTAS PARA FOTOS DE PACIENTES
    # ============================================================================
    path('fotos-paciente/', FotoPacienteListView.as_view(), name="foto_paciente_list"),
    path('fotos-paciente/crear/', FotoPacienteCreateView.as_view(), name="foto_paciente_create"),
    path('fotos-paciente/<int:pk>/editar/', FotoPacienteUpdateView.as_view(), name="foto_paciente_update"),
    path('fotos-paciente/<int:pk>/eliminar/', FotoPacienteDeleteView.as_view(), name="foto_paciente_delete"),
    path('fotos-paciente/paciente/<int:paciente_id>/', fotos_por_paciente, name="fotos_por_paciente"),
    
    # ============================================================================
    # API PARA BÚSQUEDA
    # ============================================================================
    path('paciente_find/', paciente_find, name="paciente_find"),
]
