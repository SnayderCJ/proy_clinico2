from django.contrib import admin
from .models import (
    TipoSangre, Paciente, Especialidad, Doctor, Cargo, Empleado,
    TipoMedicamento, MarcaMedicamento, Medicamento, Diagnostico,
    TipoGasto, GastoMensual, FotoPaciente
)

@admin.register(TipoSangre)
class TipoSangreAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'descripcion')
    search_fields = ('tipo', 'descripcion')

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'cedula_ecuatoriana', 'telefono', 'email', 'activo')
    list_filter = ('sexo', 'estado_civil', 'tipo_sangre', 'activo')
    search_fields = ('nombres', 'apellidos', 'cedula_ecuatoriana', 'email')
    readonly_fields = ('edad',)
    ordering = ('apellidos', 'nombres')

@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'ruc', 'codigo_unico_doctor', 'activo')
    list_filter = ('especialidad', 'activo')
    search_fields = ('nombres', 'apellidos', 'ruc', 'codigo_unico_doctor')
    filter_horizontal = ('especialidad',)

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'cedula_ecuatoriana', 'cargo', 'sueldo', 'activo')
    list_filter = ('cargo', 'activo')
    search_fields = ('nombres', 'apellidos', 'cedula_ecuatoriana')

@admin.register(TipoMedicamento)
class TipoMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')

@admin.register(MarcaMedicamento)
class MarcaMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')

@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'marca_medicamento', 'concentracion', 'cantidad', 'precio', 'activo')
    list_filter = ('tipo', 'marca_medicamento', 'via_administracion', 'comercial', 'activo')
    search_fields = ('nombre', 'descripcion')

@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'activo')
    list_filter = ('activo',)
    search_fields = ('codigo', 'descripcion')

@admin.register(TipoGasto)
class TipoGastoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')

@admin.register(GastoMensual)
class GastoMensualAdmin(admin.ModelAdmin):
    list_display = ('tipo_gasto', 'fecha', 'valor')
    list_filter = ('tipo_gasto', 'fecha')
    search_fields = ('tipo_gasto__nombre', 'observacion')
    ordering = ('-fecha',)

@admin.register(FotoPaciente)
class FotoPacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'descripcion', 'fecha_subida')
    list_filter = ('fecha_subida',)
    search_fields = ('paciente__nombres', 'paciente__apellidos', 'descripcion')
    ordering = ('-fecha_subida',)
