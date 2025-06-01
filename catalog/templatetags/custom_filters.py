from django import template

register = template.Library()


@register.filter
def clean_number(value):
    try:
        value = float(value)
        if value.is_integer():
            return int(value)
        return value
    except (ValueError, TypeError):
        return value
