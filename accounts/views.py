from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

from .forms import LoginForm, RegisterForm
from .decorators import role_required

User = get_user_model()


@require_http_methods(['GET', 'POST'])
def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if getattr(user, 'user_type', None) == User.USER_TYPE_ADMIN:
                return redirect('admin_dashboard')
            if getattr(user, 'user_type', None) == User.USER_TYPE_SUPERVISOR:
                return redirect('supervisor_dashboard')
            if getattr(user, 'user_type', None) == User.USER_TYPE_AGENT:
                return redirect('agent_dashboard')
            return redirect('/')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'accounts/login.html', {'form': form})


@require_http_methods(['GET', 'POST'])
@require_http_methods(['GET', 'POST'])
def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']
        user_type = form.cleaned_data['user_type']
        user = User.objects.create_user(email=email, password=password, user_type=user_type, is_active=False)

        # Generate activation link and store in session
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activate_url = request.build_absolute_uri(f"/accounts/activate/{uid}/{token}/")
        request.session['activation_link'] = activate_url

        messages.success(request, 'Account created. Click the activation link below to activate.')
        return redirect('login')
    return render(request, 'accounts/register.html', {'form': form})


@require_http_methods(['GET'])
def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account activated. You can now log in.')
        return redirect('login')
    messages.error(request, 'Activation link invalid.')
    return redirect('register')


@require_http_methods(['GET', 'POST'])
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@require_http_methods(['GET'])
@role_required(User.USER_TYPE_ADMIN)
def admin_dashboard(request):
    """Very small example dashboard views. They check that the user is
    authenticated and has the expected `user_type`. In a real app you
    should use decorators and more robust permission checks.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    if getattr(request.user, 'user_type', None) != User.USER_TYPE_ADMIN:
        messages.error(request, 'Access denied: admin only.')
        return redirect('login')
    return render(request, 'accounts/dashboard_admin.html')


@require_http_methods(['GET'])
@role_required(User.USER_TYPE_SUPERVISOR)
def supervisor_dashboard(request):
    return render(request, 'accounts/dashboard_supervisor.html')


@require_http_methods(['GET'])
@role_required(User.USER_TYPE_AGENT)
def agent_dashboard(request):
    return render(request, 'accounts/dashboard_agent.html')