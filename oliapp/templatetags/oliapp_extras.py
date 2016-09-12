from django import template

register = template.Library()


@register.simple_tag
def concat(*args):
    return ''.join(map(str, args))


@register.simple_tag
def isodate(date, fmt=None):
    try:
        return date.strftime('%Y-%m-%d')
    except AttributeError:
        return ''
