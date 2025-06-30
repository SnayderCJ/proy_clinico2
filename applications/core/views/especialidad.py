from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from applications.core.models import Especialidad
from applications.core.forms.especialidad import EspecialidadForm
from applications.security.components.mixin_crud import PermissionMixin


class EspecialidadListView(PermissionMixin, LoginRequiredMixin, ListView):
    """Vista para listar todas las especialidades médicas"""
    
    model = Especialidad
    template_name = "core/especialidades/list.html"
    context_object_name = "especialidades"
    paginate_by = 20
    permission_required = "view_especialidad"

    def get_queryset(self):
        queryset = Especialidad.objects.all()
        
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
        context["total_especialidades"] = Especialidad.objects.count()
        context["especialidades_activas"] = Especialidad.objects.filter(activo=True).count()
        return context


class EspecialidadCreateView(PermissionMixin, LoginRequiredMixin, CreateView):
    """Vista para crear una nueva especialidad médica"""
    
    model = Especialidad
    form_class = EspecialidadForm
    template_name = "core/especialidades/form.html"
    success_url = reverse_lazy("core:especialidad_list")
    permission_required = "add_especialidad"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Especialidad '{self.object.nombre}' creada exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al crear la especialidad. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class EspecialidadUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    """Vista para actualizar una especialidad médica"""
    
    model = Especialidad
    form_class = EspecialidadForm
    template_name = "core/especialidades/form.html"
    success_url = reverse_lazy("core:especialidad_list")
    permission_required = "change_especialidad"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Especialidad '{self.object.nombre}' actualizada exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al actualizar la especialidad. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class EspecialidadDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar una especialidad médica"""
    
    model = Especialidad
    template_name = "components/delete.html"
    success_url = reverse_lazy("core:especialidad_list")
    permission_required = "delete_especialidad"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Eliminar Especialidad"
        context["description"] = f"¿Está seguro de que desea eliminar la especialidad '{self.object.nombre}'?"
        context["back_url"] = self.success_url
        
        # Verificar si hay doctores asociados
        doctores_count = self.object.especialidades.count()
        if doctores_count > 0:
            context["has_dependencies"] = True
            context["dependencies_message"] = f"Esta especialidad está asociada a {doctores_count} doctor(es). No se puede eliminar."
        
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar dependencias antes de eliminar
        if self.object.especialidades.exists():
            messages.error(
                request,
                f"No se puede eliminar la especialidad '{self.object.nombre}' porque está asociada a uno o más doctores."
            )
            return redirect(self.success_url)
        
        nombre = self.object.nombre
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f"Especialidad '{nombre}' eliminada exitosamente."
        )
        return response
