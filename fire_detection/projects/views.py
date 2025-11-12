from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Project
from .forms import ProjectCreationForm
from accounts.models import CustomUser

@login_required
def create_project(request):
    # Vérifier que l'utilisateur est un superviseur
    if request.user.user_type != CustomUser.USER_TYPE_SUPERVISOR:
        return HttpResponseForbidden("Access denied")
    
    if request.method == 'POST':
        form = ProjectCreationForm(request.POST, supervisor=request.user)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('projects:project_list')
    else:
        form = ProjectCreationForm(supervisor=request.user)
    
    return render(request, 'projects/create_project.html', {'form': form})

@login_required
def project_list(request):
    if request.user.user_type != CustomUser.USER_TYPE_SUPERVISOR:
        return HttpResponseForbidden("Access denied")
    
    # Récupérer les projets créés par ce superviseur
    projects = Project.objects.filter(supervisor=request.user)
    
    return render(request, 'projects/project_list.html', {'projects': projects})

@login_required
def project_detail(request, project_id):
    if request.user.user_type != CustomUser.USER_TYPE_SUPERVISOR:
        return HttpResponseForbidden("Access denied")
    
    project = get_object_or_404(Project, id=project_id, supervisor=request.user)
    return render(request, 'projects/project_detail.html', {'project': project})