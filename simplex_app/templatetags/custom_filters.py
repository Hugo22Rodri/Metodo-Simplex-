from django import template

register = template.Library()

@register.filter
def make_range(value):
    """Crea un rango de 0 a value-1."""
    return range(value)

@register.filter
def get_item(lst, index):
    """Obtiene un elemento de una lista por su índice."""
    try:
        return lst[index]
    except (IndexError, TypeError):
        return None

@register.filter
def subtract(value, arg):
    """Resta el valor arg a value (ambos convertidos a int). Si falla, devuelve 0."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0
