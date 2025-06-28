from django.contrib import admin
from .models import (
    HorarioAtencion, CitaMedica, Atencion, DetalleAtencion,
    ServiciosAdicionales, Pago, DetallePago
)

@admin.register(HorarioAtencion)
class HorarioAtencionAdmin(admin.ModelAdmin):
    list_display = ('dia_semana', 'hora_inicio', 'hora_fin', 'activo')
    list_filter = ('dia_semana', 'activo')
    search_fields = ('dia_semana',)

@admin.register(CitaMedica)
class CitaMedicaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'fecha', 'hora_cita', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('paciente__nombres', 'paciente__apellidos')
    date_hierarchy = 'fecha'

@admin.register(Atencion)
class AtencionAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'fecha_atencion', 'es_control')
    list_filter = ('es_control', 'fecha_atencion')
    search_fields = ('paciente__nombres', 'paciente__apellidos', 'motivo_consulta')
    filter_horizontal = ('diagnostico',)
    readonly_fields = ('fecha_atencion',)
    date_hierarchy = 'fecha_atencion'

@admin.register(DetalleAtencion)
class DetalleAtencionAdmin(admin.ModelAdmin):
    list_display = ('atencion', 'medicamento', 'cantidad', 'duracion_tratamiento')
    list_filter = ('medicamento',)
    search_fields = ('atencion__paciente__nombres', 'medicamento__nombre')

@admin.register(ServiciosAdicionales)
class ServiciosAdicionalesAdmin(admin.ModelAdmin):
    list_display = ('nombre_servicio', 'costo_servicio', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre_servicio', 'descripcion')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'atencion', 'metodo_pago', 'monto_total', 'estado', 'fecha_pago')
    list_filter = ('estado', 'metodo_pago', 'fecha_creacion')
    search_fields = ('atencion__paciente__nombres', 'nombre_pagador')
    readonly_fields = ('fecha_creacion',)
    date_hierarchy = 'fecha_creacion'

@admin.register(DetallePago)
class DetallePagoAdmin(admin.ModelAdmin):
    list_display = ('pago', 'servicio_adicional', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('aplica_seguro',)
    search_fields = ('pago__atencion__paciente__nombres', 'servicio_adicional__nombre_servicio')
    readonly_fields = ('subtotal',)
