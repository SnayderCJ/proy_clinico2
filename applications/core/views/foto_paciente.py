from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from applications.core.models import FotoPaciente, Paciente
from applications.core.forms.foto_paciente import FotoPacienteForm
from applications.security.components.mixin_crud import PermissionMixin


class FotoPacienteListView(PermissionMixin, LoginRequiredMixin, ListView):
    """Vista para listar todas las fotos de pacientes"""
    
    model = FotoPaciente
    template_name = "core/fotos_paciente/list.html"
    context_object_name = "fotos_paciente"
    paginate_by = 12  # Mostrar 12 fotos por página
    permission_required = "view_fotopaciente"

    def get_queryset(self):
        queryset = FotoPaciente.objects.select_related('paciente').all()
        
        # Filtro por paciente específico
        paciente_id = self.request.GET.get("paciente")
        if paciente_id:
            queryset = queryset.filter(paciente__id=paciente_id)
        
        # Filtro de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(paciente__nombres__icontains=search) | 
                Q(paciente__apellidos__icontains=search) |
                Q(descripcion__icontains=search)
            )
        
        return queryset.order_by("-fecha_subida")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["paciente_selected"] = self.request.GET.get("paciente", "")
        
        # Si hay un paciente seleccionado, obtener sus datos
        paciente_id = self.request.GET.get("paciente")
        if paciente_id:
            try:
                context["paciente_actual"] = Paciente.objects.get(id=paciente_id, activo=True)
            except Paciente.DoesNotExist:
                context["paciente_actual"] = None
        
        context["total_fotos"] = FotoPaciente.objects.count()
        
        # Pacientes con fotos para el filtro
        pacientes_con_fotos = Paciente.objects.filter(
            fotos__isnull=False, 
            activo=True
        ).distinct().order_by('apellidos', 'nombres')
        context["pacientes_con_fotos"] = pacientes_con_fotos
        
        return context


class FotoPacienteCreateView(PermissionMixin, LoginRequiredMixin, CreateView):
    """Vista para subir una nueva foto de paciente"""
    
    model = FotoPaciente
    form_class = FotoPacienteForm
    template_name = "core/fotos_paciente/form.html"
    permission_required = "add_fotopaciente"

    def get_success_url(self):
        # Redirigir a la lista de fotos del paciente
        return reverse_lazy("core:foto_paciente_list") + f"?paciente={self.object.paciente.id}"

    def get_initial(self):
        initial = super().get_initial()
        # Si se pasa un paciente en la URL, preseleccionarlo
        paciente_id = self.request.GET.get('paciente')
        if paciente_id:
            try:
                paciente = Paciente.objects.get(id=paciente_id, activo=True)
                initial['paciente'] = paciente
            except Paciente.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Si hay un paciente preseleccionado, agregarlo al contexto
        paciente_id = self.request.GET.get('paciente')
        if paciente_id:
            try:
                context["paciente_preseleccionado"] = Paciente.objects.get(id=paciente_id, activo=True)
            except Paciente.DoesNotExist:
                pass
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Foto del paciente {self.object.paciente.nombre_completo} subida exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al subir la foto. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class FotoPacienteUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    """Vista para actualizar la descripción de una foto de paciente"""
    
    model = FotoPaciente
    form_class = FotoPacienteForm
    template_name = "core/fotos_paciente/form.html"
    permission_required = "change_fotopaciente"

    def get_success_url(self):
        # Redirigir a la lista de fotos del paciente
        return reverse_lazy("core:foto_paciente_list") + f"?paciente={self.object.paciente.id}"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Deshabilitar el campo de paciente e imagen en edición
        form.fields['paciente'].widget.attrs['readonly'] = True
        form.fields['imagen'].widget.attrs['readonly'] = True
        form.fields['paciente'].disabled = True
        form.fields['imagen'].disabled = True
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Descripción de la foto actualizada exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al actualizar la descripción. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class FotoPacienteDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar una foto de paciente"""
    
    model = FotoPaciente
    template_name = "components/delete.html"
    permission_required = "delete_fotopaciente"

    def get_success_url(self):
        # Redirigir a la lista de fotos del paciente
        return reverse_lazy("core:foto_paciente_list") + f"?paciente={self.object.paciente.id}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Eliminar Foto"
        context["description"] = f"¿Está seguro de que desea eliminar esta foto del paciente {self.object.paciente.nombre_completo}?"
        context["back_url"] = self.get_success_url()
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        paciente_nombre = self.object.paciente.nombre_completo
        
        # Eliminar el archivo físico
        if self.object.imagen:
            try:
                self.object.imagen.delete(save=False)
            except:
                pass  # Si no se puede eliminar el archivo, continuar
        
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f"Foto del paciente {paciente_nombre} eliminada exitosamente."
        )
        return response


# Vista adicional para mostrar fotos de un paciente específico
def fotos_por_paciente(request, paciente_id):
    """Vista para mostrar todas las fotos de un paciente específico"""
    paciente = get_object_or_404(Paciente, id=paciente_id, activo=True)
    
    # Redirigir a la lista general con filtro de paciente
    return redirect(f"{reverse_lazy('core:foto_paciente_list')}?paciente={paciente_id}")
