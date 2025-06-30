from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from applications.core.models import TipoSangre
from applications.core.forms.tipo_sangre import TipoSangreForm
from applications.security.components.mixin_crud import PermissionMixin


class TipoSangreListView(PermissionMixin, LoginRequiredMixin, ListView):
    """Vista para listar todos los tipos de sangre"""
    
    model = TipoSangre
    template_name = "core/tipos_sangre/list.html"
    context_object_name = "tipos_sangre"
    paginate_by = 20
    permission_required = "view_tiposangre"

    def get_queryset(self):
        queryset = TipoSangre.objects.all()
        
        # Filtro de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(tipo__icontains=search) | Q(descripcion__icontains=search)
            )
        
        return queryset.order_by("tipo")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["total_tipos"] = TipoSangre.objects.count()
        return context


class TipoSangreCreateView(PermissionMixin, LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo tipo de sangre"""
    
    model = TipoSangre
    form_class = TipoSangreForm
    template_name = "core/tipos_sangre/form.html"
    success_url = reverse_lazy("core:tipo_sangre_list")
    permission_required = "add_tiposangre"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Tipo de sangre '{self.object.tipo}' creado exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al crear el tipo de sangre. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class TipoSangreUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    """Vista para actualizar un tipo de sangre"""
    
    model = TipoSangre
    form_class = TipoSangreForm
    template_name = "core/tipos_sangre/form.html"
    success_url = reverse_lazy("core:tipo_sangre_list")
    permission_required = "change_tiposangre"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Tipo de sangre '{self.object.tipo}' actualizado exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al actualizar el tipo de sangre. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class TipoSangreDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar un tipo de sangre"""
    
    model = TipoSangre
    template_name = "components/delete.html"
    success_url = reverse_lazy("core:tipo_sangre_list")
    permission_required = "delete_tiposangre"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Eliminar Tipo de Sangre"
        context["description"] = f"¿Está seguro de que desea eliminar el tipo de sangre '{self.object.tipo}'?"
        context["back_url"] = self.success_url
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        tipo = self.object.tipo
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f"Tipo de sangre '{tipo}' eliminado exitosamente."
        )
        return response
