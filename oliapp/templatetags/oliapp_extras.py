from django import template

register = template.Library()


@register.simple_tag
def concat(*args):
    return ''.join(map(str, args))


@register.simple_tag
def isodate(date, fmt='%Y-%m-%d'):
    try:
        return date.strftime(fmt)
    except AttributeError:
        return ''


@register.simple_tag(takes_context=True)
def seqmask(context, seq, is_public):
    if context.request.user.is_authenticated or is_public:
        return seq
    else:
        return 'N' * len(seq)