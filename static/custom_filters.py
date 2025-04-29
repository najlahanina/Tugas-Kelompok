from django import template

register = template.Library()

@register.filter
def split(value, separator=","):
    if value:
        return [v.strip() for v in value.split(separator)]
    return []
