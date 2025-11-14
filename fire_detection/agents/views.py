from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .forms import AgentCreationForm, AgentProfileForm
from accounts.models import CustomUser

# agents/views.py
@login_required
def add_agent(request):
    if request.user.user_type != CustomUser.USER_TYPE_SUPERVISOR:
        return HttpResponseForbidden("Access denied")
    
    if request.method == 'POST':
        user_form = AgentCreationForm(request.POST)
        profile_form = AgentProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Sauvegarder l'utilisateur agent
            agent_user = user_form.save()
            
            # Sauvegarder le profil agent (sans commit pour lier l'user)
            agent_profile = profile_form.save(commit=False)
            agent_profile.user = agent_user  # Lier le profil à l'utilisateur
            agent_profile.save()  # Maintenant sauvegarder
            
            messages.success(request, f'Agent {agent_user.email} created successfully!')
            return redirect('supervisor_dashboard')
    
    else:
        user_form = AgentCreationForm()
        profile_form = AgentProfileForm()
    
    return render(request, 'agents/add_agent.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def agent_list(request):
    # Vérifier que l'utilisateur est un superviseur
    if request.user.user_type != CustomUser.USER_TYPE_SUPERVISOR:
        return HttpResponseForbidden("Access denied")
    
    # Récupérer tous les agents avec leurs profils
    agents = CustomUser.objects.filter(
        user_type=CustomUser.USER_TYPE_AGENT
    ).select_related('agentprofile')
    
    # Calculate statistics
    total_agents = agents.count()
    active_accounts = agents.filter(is_active=True).count()
    active_profiles = sum(1 for agent in agents if hasattr(agent, 'agentprofile') and agent.agentprofile and agent.agentprofile.is_active)
    inactive_count = total_agents - active_accounts
    
    context = {
        'agents': agents,
        'total_agents': total_agents,
        'active_accounts': active_accounts,
        'active_profiles': active_profiles,
        'inactive_count': inactive_count,
    }
    
    return render(request, 'agents/agent_list.html', context)