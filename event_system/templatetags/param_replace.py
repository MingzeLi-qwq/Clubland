# event_system/templatetags/param_replace.py
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    request = context['request']
    params = request.GET.copy()
    
    for key, value in kwargs.items():
        if value:
            params[key] = value
        else:
            if key in params:
                del params[key]
    return params.urlencode()