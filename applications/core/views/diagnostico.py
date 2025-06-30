from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from applications.core.models import Diagnostico
from applications.core.forms.diagnostico import DiagnosticoForm
from applications.security.components.mixin_crud import PermissionMixin


class DiagnosticoListView(PermissionMixin, LoginRequiredMixin, ListView):
    """Vista para listar todos los diagnósticos"""
    
    model = Diagnostico
    template_name = "core/diagnosticos/list.html"
    context_object_name = "diagnosticos"
    paginate_by = 20
    permission_required = "view_diagnostico"

    def get_queryset(self):
        queryset = Diagnostico.objects.all()
        
        # Filtro de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(codigo__icontains=search) | 
                Q(descripcion__icontains=search) |
                Q(datos_adicionales__icontains=search)
            )
        
        # Filtro por estado activo
        activo = self.request.GET.get("activo")
        if activo:
            queryset = queryset.filter(activo=activo == "true")
        
        return queryset.order_by("codigo")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["activo_selected"] = self.request.GET.get("activo", "")
        context["total_diagnosticos"] = Diagnostico.objects.count()
        context["diagnosticos_activos"] = Diagnostico.objects.filter(activo=True).count()
        return context


class DiagnosticoCreateView(PermissionMixin, LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo diagnóstico"""
    
    model = Diagnostico
    form_class = DiagnosticoForm
    template_name = "core/diagnosticos/form.html"
    success_url = reverse_lazy("core:diagnostico_list")
    permission_required = "add_diagnostico"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Diagnóstico '{self.object.codigo} - {self.object.descripcion}' creado exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al crear el diagnóstico. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class DiagnosticoUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    """Vista para actualizar un diagnóstico"""
    
    model = Diagnostico
    form_class = DiagnosticoForm
    template_name = "core/diagnosticos/form.html"
    success_url = reverse_lazy("core:diagnostico_list")
    permission_required = "change_diagnostico"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Diagnóstico '{self.object.codigo} - {self.object.descripcion}' actualizado exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al actualizar el diagnóstico. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class DiagnosticoDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar un diagnóstico"""
    
    model = Diagnostico
    template_name = "components/delete.html"
    success_url = reverse_lazy("core:diagnostico_list")
    permission_required = "delete_diagnostico"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Eliminar Diagnóstico"
        context["description"] = f"¿Está seguro de que desea eliminar el diagnóstico '{self.object.codigo} - {self.object.descripcion}'?"
        context["back_url"] = self.success_url
        
        # Verificar si hay atenciones médicas asociadas
        try:
            from applications.doctor.models import Atencion
            atenciones_count = Atencion.objects.filter(diagnostico=self.object).count()
            if atenciones_count > 0:
                context["has_dependencies"] = True
                context["dependencies_message"] = f"Este diagnóstico está asociado a {atenciones_count} atención(es) médica(s). No se puede eliminar."
        except:
            pass
        
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar dependencias antes de eliminar
        try:
            from applications.doctor.models import Atencion
            if Atencion.objects.filter(diagnostico=self.object).exists():
                messages.error(
                    request,
                    f"No se puede eliminar el diagnóstico '{self.object.codigo}' porque está asociado a una o más atenciones médicas."
                )
                return redirect(self.success_url)
        except:
            pass
        
        codigo = self.object.codigo
        descripcion = self.object.descripcion
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f"Diagnóstico '{codigo} - {descripcion}' eliminado exitosamente."
        )
        return response
