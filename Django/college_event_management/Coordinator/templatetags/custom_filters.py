from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, list) and len(dictionary) > key:
        return dictionary[key]
    elif isinstance(dictionary, dict):
        return dictionary.get(key)
    return None