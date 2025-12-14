from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Split a string by a delimiter"""
    if value:
        return value.split(arg)
    return []

@register.filter
def get_country_code(value):
    """Extract country code from birth_place value"""
    if value and '|' in value:
        parts = value.split('|')
        return parts[1] if len(parts) > 1 else ''
    return ''

@register.filter
def get_country_name(value):
    """Extract country name from birth_place value"""
    if value and '|' in value:
        parts = value.split('|')
        return parts[0] if len(parts) > 0 else value
    return value
