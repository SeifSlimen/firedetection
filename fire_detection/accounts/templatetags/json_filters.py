# À placer dans: votre_app/templatetags/json_filters.py

from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def json_dumps(value):
    """
    Convert a Python object to a JSON string.
    Usage in template: {{ my_data|json_dumps }}
    """
    if value is None:
        return 'null'
    return json.dumps(value, ensure_ascii=False)


@register.filter(is_safe=True)
def json_script(value):
    """
    Convert a Python object to a JSON string safe for use in <script> tags.
    Prevents XSS attacks by escaping dangerous characters.
    Usage in template: {{ my_data|json_script }}
    """
    if value is None:
        return mark_safe('null')
    
    # Convert to JSON with proper escaping
    json_str = json.dumps(value, ensure_ascii=False)
    
    # Escape characters that could break out of script tags
    json_str = (
        json_str.replace('<', '\\u003C')
                .replace('>', '\\u003E')
                .replace('&', '\\u0026')
    )
    
    return mark_safe(json_str)


@register.filter
def get_coords(zone):
    """
    Extract and parse coordinates from a zone object.
    Returns a Python list/dict ready for json_dumps.
    Usage: {{ zone|get_coords|json_dumps }}
    """
    if not zone or not hasattr(zone, 'coords_polys'):
        return []
    
    coords = zone.coords_polys
    
    # If already a list/dict, return it
    if isinstance(coords, (list, dict)):
        return coords
    
    # If string, try to parse JSON
    if isinstance(coords, str) and coords:
        try:
            return json.loads(coords)
        except json.JSONDecodeError:
            return []
    
    return []