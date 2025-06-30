from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from applications.core.models import Doctor, Especialidad
from applications.core.forms.doctor import DoctorForm
from applications.security.components.mixin_crud import PermissionMixin


class DoctorListView(PermissionMixin, LoginRequiredMixin, ListView):
    """Vista para listar todos los doctores"""
    
    model = Doctor
    template_name = "core/doctores/list.html"
    context_object_name = "doctores"
    paginate_by = 20
    permission_required = "view_doctor"

    def get_queryset(self):
        queryset = Doctor.objects.prefetch_related('especialidad').all()
        
        # Filtro de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombres__icontains=search) | 
                Q(apellidos__icontains=search) |
                Q(ruc__icontains=search) |
                Q(codigo_unico_doctor__icontains=search)
            )
        
        # Filtro por especialidad
        especialidad = self.request.GET.get("especialidad")
        if especialidad:
            queryset = queryset.filter(especialidad__id=especialidad)
        
        # Filtro por estado activo
        activo = self.request.GET.get("activo")
        if activo:
            queryset = queryset.filter(activo=activo == "true")
        
        return queryset.order_by("apellidos", "nombres")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["especialidad_selected"] = self.request.GET.get("especialidad", "")
        context["activo_selected"] = self.request.GET.get("activo", "")
        context["especialidades"] = Especialidad.objects.filter(activo=True)
        context["total_doctores"] = Doctor.objects.count()
        context["doctores_activos"] = Doctor.objects.filter(activo=True).count()
        return context


class DoctorDetailView(PermissionMixin, LoginRequiredMixin, DetailView):
    """Vista para mostrar detalles completos de un doctor"""
    
    model = Doctor
    template_name = "core/doctores/detail.html"
    context_object_name = "doctor"
    permission_required = "view_doctor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.get_object()
        
        # Obtener estadísticas del doctor
        try:
            # Total de atenciones realizadas
            context["total_atenciones"] = doctor.atenciones.count()
            
            # Atenciones recientes
            context["atenciones_recientes"] = doctor.atenciones.all()[:5]
            
            # Citas programadas
            from datetime import date
            context["citas_programadas"] = doctor.citas.filter(
                fecha__gte=date.today()
            ).exclude(estado="cancelada").count()
            
        except:
            context["total_atenciones"] = 0
            context["atenciones_recientes"] = []
            context["citas_programadas"] = 0
        
        return context


class DoctorCreateView(PermissionMixin, LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo doctor"""
    
    model = Doctor
    form_class = DoctorForm
    template_name = "core/doctores/form.html"
    success_url = reverse_lazy("core:doctor_list")
    permission_required = "add_doctor"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Doctor {self.object.nombre_completo} creado exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al crear el doctor. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class DoctorUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    """Vista para actualizar datos de un doctor"""
    
    model = Doctor
    form_class = DoctorForm
    template_name = "core/doctores/form.html"
    permission_required = "change_doctor"

    def get_success_url(self):
        return reverse_lazy("core:doctor_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Datos del doctor {self.object.nombre_completo} actualizados exitosamente."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error al actualizar el doctor. Verifique los datos ingresados."
        )
        return super().form_invalid(form)


class DoctorDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar (desactivar) un doctor"""
    
    model = Doctor
    template_name = "components/delete.html"
    success_url = reverse_lazy("core:doctor_list")
    permission_required = "delete_doctor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Eliminar Doctor"
        context["description"] = f"¿Está seguro de que desea eliminar al doctor {self.object.nombre_completo}?"
        context["back_url"] = self.success_url
        
        # Verificar si hay atenciones asociadas
        try:
            atenciones_count = self.object.atenciones.count()
            if atenciones_count > 0:
                context["has_dependencies"] = True
                context["dependencies_message"] = f"Este doctor tiene {atenciones_count} atención(es) registrada(s). Se desactivará en lugar de eliminarse."
        except:
            pass
        
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre_completo
        
        # Verificar si tiene atenciones asociadas
        try:
            if self.object.atenciones.exists():
                # No eliminar físicamente, solo desactivar
                self.object.activo = False
                self.object.save()
                messages.success(
                    request,
                    f"Doctor {nombre} desactivado exitosamente."
                )
                return redirect(self.success_url)
        except:
            pass
        
        # Si no tiene dependencias, eliminar físicamente
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f"Doctor {nombre} eliminado exitosamente."
        )
        return response
