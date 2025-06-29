from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from applications.security.components.menu_module import MenuModule
from applications.security.components.mixin_crud import PermissionMixin
from applications.security.models import GroupModulePermission


class ModuloTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"
    login_url = "/security/signin/"

    def dispatch(self, request, *args, **kwargs):
        # Manejar cambio de grupo si se proporciona gpid
        if request.GET.get("gpid"):
            group_id = request.GET.get("gpid")
            # Verificar que el usuario pertenece a este grupo
            if request.user.groups.filter(id=group_id).exists():
                request.session["group_id"] = int(group_id)
                return redirect("home")

        # Si no hay grupo en sesión, establecer el primero disponible
        if not request.session.get("group_id") and request.user.groups.exists():
            first_group = request.user.groups.first()
            request.session["group_id"] = first_group.id

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Información básica
        context["title"] = "SaludTotal - Dashboard"
        context["title1"] = "Panel de Control"

        # Obtener grupo activo
        group_id = self.request.session.get("group_id")
        current_group = None
        if group_id:
            current_group = self.request.user.groups.filter(id=group_id).first()

        # Estadísticas del rol
        user_stats = self.get_user_role_stats(group_id)

        context.update(
            {
                "current_group": current_group,
                "user_stats": user_stats,
                "available_modules": self.get_available_modules(group_id),
                "role_name": current_group.name if current_group else "Sin Rol",
            }
        )

        # Llenar menús usando el componente existente
        MenuModule(self.request).fill(context)

        return context

    def get_user_role_stats(self, group_id):
        """Obtiene estadísticas según el rol del usuario"""
        if not group_id:
            return {}

        # Importar modelos aquí para evitar importaciones circulares
        from applications.core.models import Paciente, Doctor, Empleado

        stats = {"total_modules": 0, "role_specific_stats": {}}

        # Contar módulos disponibles
        stats["total_modules"] = GroupModulePermission.objects.filter(
            group_id=group_id, module__is_active=True
        ).count()

        # Estadísticas específicas por rol
        try:
            group_name = self.request.user.groups.get(id=group_id).name

            if "Administrador" in group_name:
                stats["role_specific_stats"] = {
                    "total_users": self.request.user.__class__.objects.count(),
                    "total_patients": Paciente.objects.count(),
                    "total_doctors": Doctor.objects.count(),
                    "total_employees": Empleado.objects.count(),
                }
            elif "Doctor" in group_name:
                stats["role_specific_stats"] = {
                    "total_patients": Paciente.objects.count(),
                    "active_patients": Paciente.active_patient.count(),
                    "total_doctors": Doctor.objects.count(),
                }
            elif "Secretaria" in group_name:
                stats["role_specific_stats"] = {
                    "total_patients": Paciente.objects.count(),
                    "total_employees": Empleado.objects.count(),
                    "total_doctors": Doctor.objects.count(),
                }
            elif "Recepcionista" in group_name:
                stats["role_specific_stats"] = {
                    "total_patients": Paciente.objects.count(),
                    "active_patients": Paciente.active_patient.count(),
                }
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")

        return stats

    def get_available_modules(self, group_id):
        """Obtiene los módulos disponibles para el grupo"""
        if not group_id:
            return []

        return (
            GroupModulePermission.objects.filter(
                group_id=group_id, module__is_active=True
            )
            .select_related("module", "module__menu")
            .order_by("module__menu__order", "module__order")
        )
