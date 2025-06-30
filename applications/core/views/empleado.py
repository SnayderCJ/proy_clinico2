from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from applications.core.models import Empleado, Cargo
from applications.core.forms.empleado import EmpleadoForm
from applications.security.components.mixin_crud import PermissionMixin


class EmpleadoListView(PermissionMixin, LoginRequiredMixin, ListView):
    """Vista para listar todos los empleados"""
    
    model = Empleado
    template_name = "core/empleados/list.html"
    context_object_name = "empleados"
    paginate_by = 20
    permission_required = "view_empleado"

    def get_queryset(self):
        queryset = Empleado.objects.select_related('cargo').all()
        
        # Filtro de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombres__icontains=search) | 
                Q(apellidos__icontains=search) |
                Q(cedula_ecuatoriana__icontains=search) |
                Q(cargo__nombre__icontains=search)
            )
        
        # Filtro por cargo
        cargo = self.request.GET.get("cargo")
        if cargo:
            queryset = queryset.filter(cargo__id=cargo)
        
        # Filtro por estado activo
        activo = self.request.GET.get("activo")
        if activo:
            queryset = queryset.filter(activo=activo == "true")
        
        return queryset.order_by("apellidos", "nombres")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["cargo_selected"] = self.request.GET.get("cargo", "")
        context["activo_selected"] = self.request.GET.get("activo", "")
        context["cargos"] = Cargo.objects.filter(activo=True)
        context["total_empleados"] = Empleado.objects.count()
        context["empleados_activos"] = Empleado.objects.filter(activo=True).count()
        return context


class EmpleadoDetailView(PermissionMixin, LoginRequiredMixin, DetailView):
    """Vista para mostrar detalles completos de un empleado"""
    
    model = Empleado
    template_name = "core/empleados/detail.html"
    context_object_name = "empleado"
    permission_required = "view_empleado"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empleado = self.get_object()
        
        # Calcular años de servicio
        from datetime import date
        if empleado.fecha_ingreso:
            años_servicio = (date.today() - empleado.fecha_ingreso).days // 365
            context["años_servicio"] = años_servicio
        else:
            context["años_servicio"] = 0
        
        # Calcular edad
        if empleado.fecha_nacimiento:
            edad = (date.today() - empleado.fecha_nacimiento).days // 365
            context["edad"] = edad
        else:
            context["edad"] = 0
        
        return context


class EmpleadoCreateView(PermissionMixin, LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo empleado"""
    
    model = Empleado
    form_class = EmpleadoForm
    template_name = "core/empleados/form.html"
    success_url = reverse_lazy("core:empleado_list")
    permission_required = "add_empleado"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Empleado {self.object.nombre_completo} creado exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al crear el empleado. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class EmpleadoUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    """Vista para actualizar datos de un empleado"""
    
    model = Empleado
    form_class = EmpleadoForm
    template_name = "core/empleados/form.html"
    permission_required = "change_empleado"

    def get_success_url(self):
        return reverse_lazy("core:empleado_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Datos del empleado {self.object.nombre_completo} actualizados exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al actualizar el empleado. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class EmpleadoDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar (desactivar) un empleado"""
    
    model = Empleado
    template_name = "components/delete.html"
    success_url = reverse_lazy("core:empleado_list")
    permission_required = "delete_empleado"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Eliminar Empleado"
        context["description"] = f"¿Está seguro de que desea eliminar al empleado {self.object.nombre_completo}?"
        context["back_url"] = self.success_url
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre_completo
        
        # No eliminar físicamente, solo desactivar
        self.object.activo = False
        self.object.save()
        messages.success(
            request,
            f"Empleado {nombre} desactivado exitosamente."
        )
        return redirect(self.success_url)
