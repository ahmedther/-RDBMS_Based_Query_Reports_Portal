from django import template

register = template.Library()


@register.filter
def split_dash_get_last(value, arg):
    return value.split(arg)[-1]
