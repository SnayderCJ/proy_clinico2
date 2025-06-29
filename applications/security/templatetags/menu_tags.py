from django import template
from django.db.models import Q
from applications.security.models import Menu, Module, GroupModulePermission

register = template.Library()


@register.inclusion_tag("components/dynamic_menu.html", takes_context=True)
def show_user_menu(context):
    """
    Template tag para mostrar el menú dinámico según el rol del usuario
    """
    request = context["request"]
    user = request.user

    if not user.is_authenticated:
        return {"menus": []}

    # Obtener el grupo activo del usuario
    group_id = request.session.get("group_id")
    if not group_id and user.groups.exists():
        # Si no hay grupo en sesión, usar el primer grupo del usuario
        group_id = user.groups.first().id
        request.session["group_id"] = group_id

    if not group_id:
        return {"menus": []}

    # Obtener módulos permitidos para el grupo
    group_modules = (
        GroupModulePermission.objects.filter(group_id=group_id, module__is_active=True)
        .select_related("module", "module__menu")
        .order_by("module__menu__order", "module__order")
    )

    # Organizar módulos por menú
    menus_dict = {}
    for gmp in group_modules:
        menu = gmp.module.menu
        if menu.id not in menus_dict:
            menus_dict[menu.id] = {"menu": menu, "modules": []}
        menus_dict[menu.id]["modules"].append(gmp.module)

    # Convertir a lista ordenada
    menus = list(menus_dict.values())
    menus.sort(key=lambda x: x["menu"].order)

    return {"menus": menus, "user": user, "current_url": request.path}


@register.simple_tag(takes_context=True)
def has_module_permission(context, module_url):
    """
    Verifica si el usuario tiene permiso para acceder a un módulo específico
    """
    request = context["request"]
    user = request.user

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    group_id = request.session.get("group_id")
    if not group_id:
        return False

    return GroupModulePermission.objects.filter(
        group_id=group_id, module__url=module_url, module__is_active=True
    ).exists()


@register.simple_tag
def get_user_role_name(user):
    """
    Obtiene el nombre del rol principal del usuario
    """
    if not user.is_authenticated:
        return "Invitado"

    if user.is_superuser:
        return "Super Administrador"

    # Obtener el primer grupo del usuario
    first_group = user.groups.first()
    if first_group:
        return first_group.name

    return "Sin Rol"
