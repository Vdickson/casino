from django import template

register = template.Library()

@register.filter
def absolute_value(value):
    return abs(value)