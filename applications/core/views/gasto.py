from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import redirect
from datetime import datetime, date
from applications.core.models import TipoGasto, GastoMensual
from applications.core.forms.gasto import TipoGastoForm, GastoMensualForm
from applications.security.components.mixin_crud import PermissionMixin


# ============================================================================
# VISTAS PARA TIPO DE GASTO
# ============================================================================

class TipoGastoListView(PermissionMixin, LoginRequiredMixin, ListView):
    """Vista para listar todos los tipos de gastos"""
    
    model = TipoGasto
    template_name = "core/tipos_gasto/list.html"
    context_object_name = "tipos_gasto"
    paginate_by = 20
    permission_required = "view_tipogasto"

    def get_queryset(self):
        queryset = TipoGasto.objects.all()
        
        # Filtro de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | Q(descripcion__icontains=search)
            )
        
        # Filtro por estado activo
        activo = self.request.GET.get("activo")
        if activo:
            queryset = queryset.filter(activo=activo == "true")
        
        return queryset.order_by("nombre")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["activo_selected"] = self.request.GET.get("activo", "")
        context["total_tipos"] = TipoGasto.objects.count()
        context["tipos_activos"] = TipoGasto.objects.filter(activo=True).count()
        return context


class TipoGastoCreateView(PermissionMixin, LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo tipo de gasto"""
    
    model = TipoGasto
    form_class = TipoGastoForm
    template_name = "core/tipos_gasto/form.html"
    success_url = reverse_lazy("core:tipo_gasto_list")
    permission_required = "add_tipogasto"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Tipo de gasto '{self.object.nombre}' creado exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al crear el tipo de gasto. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class TipoGastoUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    """Vista para actualizar un tipo de gasto"""
    
    model = TipoGasto
    form_class = TipoGastoForm
    template_name = "core/tipos_gasto/form.html"
    success_url = reverse_lazy("core:tipo_gasto_list")
    permission_required = "change_tipogasto"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Tipo de gasto '{self.object.nombre}' actualizado exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al actualizar el tipo de gasto. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class TipoGastoDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar un tipo de gasto"""
    
    model = TipoGasto
    template_name = "components/delete.html"
    success_url = reverse_lazy("core:tipo_gasto_list")
    permission_required = "delete_tipogasto"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Eliminar Tipo de Gasto"
        context["description"] = f"¿Está seguro de que desea eliminar el tipo de gasto '{self.object.nombre}'?"
        context["back_url"] = self.success_url
        
        # Verificar si hay gastos asociados
        gastos_count = self.object.gastos_mensuales.count()
        if gastos_count > 0:
            context["has_dependencies"] = True
            context["dependencies_message"] = f"Este tipo de gasto está asociado a {gastos_count} gasto(s) registrado(s). No se puede eliminar."
        
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar dependencias antes de eliminar
        if self.object.gastos_mensuales.exists():
            messages.error(
                request,
                f"No se puede eliminar el tipo de gasto '{self.object.nombre}' porque está asociado a uno o más gastos registrados."
            )
            return redirect(self.success_url)
        
        nombre = self.object.nombre
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f"Tipo de gasto '{nombre}' eliminado exitosamente."
        )
        return response


# ============================================================================
# VISTAS PARA GASTO MENSUAL
# ============================================================================

class GastoMensualListView(PermissionMixin, LoginRequiredMixin, ListView):
    """Vista para listar todos los gastos mensuales"""
    
    model = GastoMensual
    template_name = "core/gastos_mensuales/list.html"
    context_object_name = "gastos_mensuales"
    paginate_by = 20
    permission_required = "view_gastomensual"

    def get_queryset(self):
        queryset = GastoMensual.objects.select_related('tipo_gasto').all()
        
        # Filtro de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(tipo_gasto__nombre__icontains=search) | 
                Q(observacion__icontains=search)
            )
        
        # Filtro por tipo de gasto
        tipo_gasto = self.request.GET.get("tipo_gasto")
        if tipo_gasto:
            queryset = queryset.filter(tipo_gasto__id=tipo_gasto)
        
        # Filtro por mes y año
        mes = self.request.GET.get("mes")
        año = self.request.GET.get("año")
        if mes and año:
            queryset = queryset.filter(fecha__month=mes, fecha__year=año)
        elif año:
            queryset = queryset.filter(fecha__year=año)
        
        return queryset.order_by("-fecha")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["tipo_gasto_selected"] = self.request.GET.get("tipo_gasto", "")
        context["mes_selected"] = self.request.GET.get("mes", "")
        context["año_selected"] = self.request.GET.get("año", "")
        context["tipos_gasto"] = TipoGasto.objects.filter(activo=True)
        
        # Estadísticas
        context["total_gastos"] = GastoMensual.objects.count()
        
        # Total gastado este mes
        hoy = date.today()
        total_mes_actual = GastoMensual.objects.filter(
            fecha__month=hoy.month,
            fecha__year=hoy.year
        ).aggregate(total=Sum('valor'))['total'] or 0
        context["total_mes_actual"] = total_mes_actual
        
        # Total gastado este año
        total_año_actual = GastoMensual.objects.filter(
            fecha__year=hoy.year
        ).aggregate(total=Sum('valor'))['total'] or 0
        context["total_año_actual"] = total_año_actual
        
        # Años disponibles para el filtro
        años_disponibles = GastoMensual.objects.dates('fecha', 'year', order='DESC')
        context["años_disponibles"] = [fecha.year for fecha in años_disponibles]
        
        # Meses para el filtro
        context["meses"] = [
            (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
            (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
            (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
        ]
        
        return context


class GastoMensualCreateView(PermissionMixin, LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo gasto mensual"""
    
    model = GastoMensual
    form_class = GastoMensualForm
    template_name = "core/gastos_mensuales/form.html"
    success_url = reverse_lazy("core:gasto_mensual_list")
    permission_required = "add_gastomensual"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Gasto de {self.object.tipo_gasto.nombre} por ${self.object.valor} registrado exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al registrar el gasto. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class GastoMensualUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    """Vista para actualizar un gasto mensual"""
    
    model = GastoMensual
    form_class = GastoMensualForm
    template_name = "core/gastos_mensuales/form.html"
    success_url = reverse_lazy("core:gasto_mensual_list")
    permission_required = "change_gastomensual"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Gasto de {self.object.tipo_gasto.nombre} actualizado exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al actualizar el gasto. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class GastoMensualDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar un gasto mensual"""
    
    model = GastoMensual
    template_name = "components/delete.html"
    success_url = reverse_lazy("core:gasto_mensual_list")
    permission_required = "delete_gastomensual"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Eliminar Gasto"
        context["description"] = f"¿Está seguro de que desea eliminar el gasto de {self.object.tipo_gasto.nombre} por ${self.object.valor}?"
        context["back_url"] = self.success_url
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        tipo_gasto = self.object.tipo_gasto.nombre
        valor = self.object.valor
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f"Gasto de {tipo_gasto} por ${valor} eliminado exitosamente."
        )
        return response
