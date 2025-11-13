from django import template
import json

register = template.Library()

@register.filter
def json_dumps(value):
    """Convert a Python object to a JSON string."""
    if value is None:
        return 'null'
    return json.dumps(value)

