from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtiene un item del diccionario usando una clave"""
    return dictionary.get(key)

@register.filter
def add(value, arg):
    """Concatena dos strings"""
    return str(value) + str(arg)

@register.filter
def sub(value, arg):
    """Resta dos números"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def mul(value, arg):
    """Multiplica dos números"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.simple_tag
def get_form_field(form, field_name):
    """Obtiene un campo específico del formulario"""
    return form[field_name] if field_name in form.fields else None
