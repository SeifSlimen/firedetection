from django import template
from accounts.models import CustomUser

register = template.Library()

@register.simple_tag
def get_role_bg(user):
    """Returns Bootstrap background class based on user role"""
    if not user or not user.is_authenticated:
        return 'bg-dark'
    
    if user.user_type == CustomUser.USER_TYPE_ADMIN:
        return 'bg-primary'
    elif user.user_type == CustomUser.USER_TYPE_SUPERVISOR:
        return 'bg-success'
    elif user.user_type == CustomUser.USER_TYPE_AGENT:
        return 'bg-warning'
    return 'bg-dark'

@register.simple_tag
def get_role_text(user):
    """Returns Bootstrap text color class based on user role"""
    if not user or not user.is_authenticated:
        return 'text-dark'
    
    if user.user_type == CustomUser.USER_TYPE_ADMIN:
        return 'text-primary'
    elif user.user_type == CustomUser.USER_TYPE_SUPERVISOR:
        return 'text-success'
    elif user.user_type == CustomUser.USER_TYPE_AGENT:
        return 'text-warning'
    return 'text-dark'

@register.simple_tag
def get_role_btn(user):
    """Returns Bootstrap button class based on user role"""
    if not user or not user.is_authenticated:
        return 'btn-primary'
    
    if user.user_type == CustomUser.USER_TYPE_ADMIN:
        return 'btn-primary'
    elif user.user_type == CustomUser.USER_TYPE_SUPERVISOR:
        return 'btn-success'
    elif user.user_type == CustomUser.USER_TYPE_AGENT:
        return 'btn-warning'
    return 'btn-primary'

@register.simple_tag
def get_role_badge(user):
    """Returns Bootstrap badge class based on user role"""
    if not user or not user.is_authenticated:
        return 'bg-secondary'
    
    if user.user_type == CustomUser.USER_TYPE_ADMIN:
        return 'bg-primary'
    elif user.user_type == CustomUser.USER_TYPE_SUPERVISOR:
        return 'bg-success'
    elif user.user_type == CustomUser.USER_TYPE_AGENT:
        return 'bg-warning'
    return 'bg-secondary'

