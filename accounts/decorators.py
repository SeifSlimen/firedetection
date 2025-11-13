from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def role_required(role):
    """Decorator factory that requires the logged-in user to have a
    specific `user_type`. It composes with `login_required` so it will
    redirect anonymous users to the login page first.
    """
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if getattr(request.user, 'user_type', None) != role:
                messages.error(request, 'Access denied.')
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
