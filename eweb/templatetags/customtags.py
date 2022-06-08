from django import template
register = template.Library()

@register.filter (name='key_list')
def convert(key_list):
    b = key_list.split('|')
    return b