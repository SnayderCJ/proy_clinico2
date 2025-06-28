from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Permite acceder a valores de diccionario con claves dinámicas en templates"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []

@register.filter
def format_date_for_input(date_obj):
    """Formatea una fecha para input type='date'"""
    if date_obj:
        return date_obj.strftime('%Y-%m-%d')
    return ''

@register.filter
def format_time_for_input(time_obj):
    """Formatea una hora para input type='time'"""
    if time_obj:
        return time_obj.strftime('%H:%M')
    return ''
