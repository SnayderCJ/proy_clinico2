from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from applications.core.models import TipoMedicamento, MarcaMedicamento, Medicamento
from applications.core.forms.medicamento import TipoMedicamentoForm, MarcaMedicamentoForm, MedicamentoForm
from applications.security.components.mixin_crud import PermissionMixin


# ============================================================================
# VISTAS PARA TIPO DE MEDICAMENTO
# ============================================================================

class TipoMedicamentoListView(PermissionMixin, LoginRequiredMixin, ListView):
    """Vista para listar todos los tipos de medicamentos"""
    
    model = TipoMedicamento
    template_name = "core/tipos_medicamento/list.html"
    context_object_name = "tipos_medicamento"
    paginate_by = 20
    permission_required = "view_tipomedicamento"

    def get_queryset(self):
        queryset = TipoMedicamento.objects.all()
        
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
        context["total_tipos"] = TipoMedicamento.objects.count()
        context["tipos_activos"] = TipoMedicamento.objects.filter(activo=True).count()
        return context


class TipoMedicamentoCreateView(PermissionMixin, LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo tipo de medicamento"""
    
    model = TipoMedicamento
    form_class = TipoMedicamentoForm
    template_name = "core/tipos_medicamento/form.html"
    success_url = reverse_lazy("core:tipo_medicamento_list")
    permission_required = "add_tipomedicamento"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Tipo de medicamento '{self.object.nombre}' creado exitosamente."
        )
        return response


class TipoMedicamentoUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    """Vista para actualizar un tipo de medicamento"""
    
    model = TipoMedicamento
    form_class = TipoMedicamentoForm
    template_name = "core/tipos_medicamento/form.html"
    success_url = reverse_lazy("core:tipo_medicamento_list")
    permission_required = "change_tipomedicamento"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Tipo de medicamento '{self.object.nombre}' actualizado exitosamente."
        )
        return response


class TipoMedicamentoDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar un tipo de medicamento"""
    
    model = TipoMedicamento
    template_name = "components/delete.html"
    success_url = reverse_lazy("core:tipo_medicamento_list")
    permission_required = "delete_tipomedicamento"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Eliminar Tipo de Medicamento"
        context["description"] = f"¿Está seguro de que desea eliminar el tipo '{self.object.nombre}'?"
        context["back_url"] = self.success_url
        
        # Verificar si hay medicamentos asociados
        medicamentos_count = self.object.medicamentos_por_tipo.count()
        if medicamentos_count > 0:
            context["has_dependencies"] = True
            context["dependencies_message"] = f"Este tipo está asociado a {medicamentos_count} medicamento(s). No se puede eliminar."
        
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar dependencias antes de eliminar
        if self.object.medicamentos_por_tipo.exists():
            messages.error(
                request,
                f"No se puede eliminar el tipo '{self.object.nombre}' porque está asociado a uno o más medicamentos."
            )
            return redirect(self.success_url)
        
        nombre = self.object.nombre
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Tipo de medicamento '{nombre}' eliminado exitosamente.")
        return response


# ============================================================================
# VISTAS PARA MARCA DE MEDICAMENTO
# ============================================================================

class MarcaMedicamentoListView(PermissionMixin, LoginRequiredMixin, ListView):
    """Vista para listar todas las marcas de medicamentos"""
    
    model = MarcaMedicamento
    template_name = "core/marcas_medicamento/list.html"
    context_object_name = "marcas_medicamento"
    paginate_by = 20
    permission_required = "view_marcamedicamento"

    def get_queryset(self):
        queryset = MarcaMedicamento.objects.all()
        
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
        context["total_marcas"] = MarcaMedicamento.objects.count()
        context["marcas_activas"] = MarcaMedicamento.objects.filter(activo=True).count()
        return context


class MarcaMedicamentoCreateView(PermissionMixin, LoginRequiredMixin, CreateView):
    """Vista para crear una nueva marca de medicamento"""
    
    model = MarcaMedicamento
    form_class = MarcaMedicamentoForm
    template_name = "core/marcas_medicamento/form.html"
    success_url = reverse_lazy("core:marca_medicamento_list")
    permission_required = "add_marcamedicamento"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Marca de medicamento '{self.object.nombre}' creada exitosamente."
        )
        return response


class MarcaMedicamentoUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    """Vista para actualizar una marca de medicamento"""
    
    model = MarcaMedicamento
    form_class = MarcaMedicamentoForm
    template_name = "core/marcas_medicamento/form.html"
    success_url = reverse_lazy("core:marca_medicamento_list")
    permission_required = "change_marcamedicamento"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Marca de medicamento '{self.object.nombre}' actualizada exitosamente."
        )
        return response


class MarcaMedicamentoDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar una marca de medicamento"""
    
    model = MarcaMedicamento
    template_name = "components/delete.html"
    success_url = reverse_lazy("core:marca_medicamento_list")
    permission_required = "delete_marcamedicamento"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Eliminar Marca de Medicamento"
        context["description"] = f"¿Está seguro de que desea eliminar la marca '{self.object.nombre}'?"
        context["back_url"] = self.success_url
        
        # Verificar si hay medicamentos asociados
        medicamentos_count = self.object.medicamentos_por_marca.count()
        if medicamentos_count > 0:
            context["has_dependencies"] = True
            context["dependencies_message"] = f"Esta marca está asociada a {medicamentos_count} medicamento(s). No se puede eliminar."
        
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar dependencias antes de eliminar
        if self.object.medicamentos_por_marca.exists():
            messages.error(
                request,
                f"No se puede eliminar la marca '{self.object.nombre}' porque está asociada a uno o más medicamentos."
            )
            return redirect(self.success_url)
        
        nombre = self.object.nombre
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Marca de medicamento '{nombre}' eliminada exitosamente.")
        return response


# ============================================================================
# VISTAS PARA MEDICAMENTO
# ============================================================================

class MedicamentoListView(PermissionMixin, LoginRequiredMixin, ListView):
    """Vista para listar todos los medicamentos"""
    
    model = Medicamento
    template_name = "core/medicamentos/list.html"
    context_object_name = "medicamentos"
    paginate_by = 20
    permission_required = "view_medicamento"

    def get_queryset(self):
        queryset = Medicamento.objects.select_related('tipo', 'marca_medicamento').all()
        
        # Filtro de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | 
                Q(descripcion__icontains=search) |
                Q(tipo__nombre__icontains=search) |
                Q(marca_medicamento__nombre__icontains=search)
            )
        
        # Filtro por tipo
        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo__id=tipo)
        
        # Filtro por marca
        marca = self.request.GET.get("marca")
        if marca:
            queryset = queryset.filter(marca_medicamento__id=marca)
        
        # Filtro por estado activo
        activo = self.request.GET.get("activo")
        if activo:
            queryset = queryset.filter(activo=activo == "true")
        
        # Filtro por stock bajo (menos de 10 unidades)
        stock_bajo = self.request.GET.get("stock_bajo")
        if stock_bajo == "true":
            queryset = queryset.filter(cantidad__lt=10)
        
        return queryset.order_by("nombre")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["tipo_selected"] = self.request.GET.get("tipo", "")
        context["marca_selected"] = self.request.GET.get("marca", "")
        context["activo_selected"] = self.request.GET.get("activo", "")
        context["stock_bajo_selected"] = self.request.GET.get("stock_bajo", "")
        context["tipos_medicamento"] = TipoMedicamento.objects.filter(activo=True)
        context["marcas_medicamento"] = MarcaMedicamento.objects.filter(activo=True)
        context["total_medicamentos"] = Medicamento.objects.count()
        context["medicamentos_activos"] = Medicamento.objects.filter(activo=True).count()
        context["medicamentos_stock_bajo"] = Medicamento.objects.filter(cantidad__lt=10, activo=True).count()
        return context


class MedicamentoDetailView(PermissionMixin, LoginRequiredMixin, DetailView):
    """Vista para mostrar detalles completos de un medicamento"""
    
    model = Medicamento
    template_name = "core/medicamentos/detail.html"
    context_object_name = "medicamento"
    permission_required = "view_medicamento"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medicamento = self.get_object()
        
        # Verificar nivel de stock
        if medicamento.cantidad < 5:
            context["stock_status"] = "critico"
            context["stock_message"] = "Stock crítico"
        elif medicamento.cantidad < 10:
            context["stock_status"] = "bajo"
            context["stock_message"] = "Stock bajo"
        else:
            context["stock_status"] = "normal"
            context["stock_message"] = "Stock normal"
        
        return context


class MedicamentoCreateView(PermissionMixin, LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo medicamento"""
    
    model = Medicamento
    form_class = MedicamentoForm
    template_name = "core/medicamentos/form.html"
    success_url = reverse_lazy("core:medicamento_list")
    permission_required = "add_medicamento"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Medicamento '{self.object.nombre}' creado exitosamente."
        )
        return response


class MedicamentoUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    """Vista para actualizar un medicamento"""
    
    model = Medicamento
    form_class = MedicamentoForm
    template_name = "core/medicamentos/form.html"
    permission_required = "change_medicamento"

    def get_success_url(self):
        return reverse_lazy("core:medicamento_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Medicamento '{self.object.nombre}' actualizado exitosamente."
        )
        return response


class MedicamentoDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar (desactivar) un medicamento"""
    
    model = Medicamento
    template_name = "components/delete.html"
    success_url = reverse_lazy("core:medicamento_list")
    permission_required = "delete_medicamento"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Eliminar Medicamento"
        context["description"] = f"¿Está seguro de que desea eliminar el medicamento '{self.object.nombre}'?"
        context["back_url"] = self.success_url
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        
        # No eliminar físicamente, solo desactivar
        self.object.activo = False
        self.object.save()
        messages.success(
            request,
            f"Medicamento '{nombre}' desactivado exitosamente."
        )
        return redirect(self.success_url)
