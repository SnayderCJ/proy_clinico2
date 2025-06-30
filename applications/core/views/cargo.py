from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from applications.core.models import Cargo
from applications.core.forms.cargo import CargoForm
from applications.security.components.mixin_crud import PermissionMixin


class CargoListView(PermissionMixin, LoginRequiredMixin, ListView):
    """Vista para listar todos los cargos"""
    
    model = Cargo
    template_name = "core/cargos/list.html"
    context_object_name = "cargos"
    paginate_by = 20
    permission_required = "view_cargo"

    def get_queryset(self):
        queryset = Cargo.objects.all()
        
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
        context["total_cargos"] = Cargo.objects.count()
        context["cargos_activos"] = Cargo.objects.filter(activo=True).count()
        return context


class CargoCreateView(PermissionMixin, LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo cargo"""
    
    model = Cargo
    form_class = CargoForm
    template_name = "core/cargos/form.html"
    success_url = reverse_lazy("core:cargo_list")
    permission_required = "add_cargo"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Cargo '{self.object.nombre}' creado exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al crear el cargo. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class CargoUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    """Vista para actualizar un cargo"""
    
    model = Cargo
    form_class = CargoForm
    template_name = "core/cargos/form.html"
    success_url = reverse_lazy("core:cargo_list")
    permission_required = "change_cargo"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Cargo '{self.object.nombre}' actualizado exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al actualizar el cargo. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class CargoDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar un cargo"""
    
    model = Cargo
    template_name = "components/delete.html"
    success_url = reverse_lazy("core:cargo_list")
    permission_required = "delete_cargo"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Eliminar Cargo"
        context["description"] = f"¿Está seguro de que desea eliminar el cargo '{self.object.nombre}'?"
        context["back_url"] = self.success_url
        
        # Verificar si hay empleados asociados
        empleados_count = self.object.cargos.count()
        if empleados_count > 0:
            context["has_dependencies"] = True
            context["dependencies_message"] = f"Este cargo está asociado a {empleados_count} empleado(s). No se puede eliminar."
        
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar dependencias antes de eliminar
        if self.object.cargos.exists():
            messages.error(
                request,
                f"No se puede eliminar el cargo '{self.object.nombre}' porque está asociado a uno o más empleados."
            )
            return redirect(self.success_url)
        
        nombre = self.object.nombre
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f"Cargo '{nombre}' eliminado exitosamente."
        )
        return response
