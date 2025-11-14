from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Q
from django.urls import reverse
from .models import Project
from django import forms

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


@require_http_methods(['GET', 'POST'])
@role_required(User.USER_TYPE_ADMIN)
def manage_users(request):
    # Actions: activate, deactivate, delete, update
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        try:
            target_user = User.objects.get(pk=user_id)
            if action == 'activate':
                target_user.is_active = True
                target_user.save()
                messages.success(request, f"User {target_user.email} activated.")
            elif action == 'deactivate':
                target_user.is_active = False
                target_user.save()
                messages.success(request, f"User {target_user.email} deactivated.")
            elif action == 'delete':
                target_user.delete()
                messages.success(request, "User deleted.")
            elif action == 'update':
                # Update user fields from form
                new_email = request.POST.get('edit_email')
                new_user_type = request.POST.get('edit_user_type')
                if new_email:
                    target_user.email = new_email
                if new_user_type:
                    target_user.user_type = new_user_type
                target_user.save()
                messages.success(request, "User updated.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    # Tri et recherche
    sort = request.GET.get('sort', 'email')
    search = request.GET.get('search', '')
    users = User.objects.all()
    if search:
        users = users.filter(Q(email__icontains=search) | Q(user_type__icontains=search))
    users = users.order_by(sort)

    # Edit form: if ?edit=<user_id> in GET, show edit form for that user
    edit_user = None
    if 'edit' in request.GET:
        try:
            edit_user = User.objects.get(pk=request.GET['edit'])
        except User.DoesNotExist:
            edit_user = None

    return render(request, 'accounts/manage_users.html', {
        'users': users,
        'sort': sort,
        'search': search,
        'edit_user': edit_user,
        'user_type_choices': User.USER_TYPE_CHOICES,
    })


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'status']


@require_http_methods(['GET', 'POST'])
@role_required(User.USER_TYPE_ADMIN)
def manage_projects(request):
    # Actions: create, update, activate, deactivate, delete
    if request.method == 'POST':
        action = request.POST.get('action')
        project_id = request.POST.get('project_id')
        if action == 'create':
            form = ProjectForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Project created.")
                return redirect('manage_projects')
        elif project_id:
            try:
                project = Project.objects.get(pk=project_id)
                if action == 'activate':
                    project.status = Project.STATUS_ACTIVE
                    project.save()
                    messages.success(request, f"Project '{project.name}' activated.")
                elif action == 'deactivate':
                    project.status = Project.STATUS_INACTIVE
                    project.save()
                    messages.success(request, f"Project '{project.name}' deactivated.")
                elif action == 'delete':
                    project.delete()
                    messages.success(request, "Project deleted.")
                elif action == 'update':
                    form = ProjectForm(request.POST, instance=project)
                    if form.is_valid():
                        form.save()
                        messages.success(request, "Project updated.")
                        return redirect('manage_projects')
            except Project.DoesNotExist:
                messages.error(request, "Project not found.")

    # Recherche et tri
    sort = request.GET.get('sort', 'created_at')
    search = request.GET.get('search', '')
    projects = Project.objects.all()
    if search:
        projects = projects.filter(name__icontains=search)
    projects = projects.order_by(sort)

    # Edit form: if ?edit=<project_id> in GET, show edit form for that project
    edit_project = None
    if 'edit' in request.GET:
        try:
            edit_project = Project.objects.get(pk=request.GET['edit'])
        except Project.DoesNotExist:
            edit_project = None

    # Formulaire de création ou d'édition
    if edit_project:
        form = ProjectForm(instance=edit_project)
    else:
        form = ProjectForm()

    return render(request, 'accounts/manage_projects.html', {
        'projects': projects,
        'sort': sort,
        'search': search,
        'edit_project': edit_project,
        'form': form,
    })