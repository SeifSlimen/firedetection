from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
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
            # Create agent user as inactive
            agent_user = user_form.save()
            agent_user.is_active = False
            agent_user.save()
            
            # Save agent profile
            agent_profile = profile_form.save(commit=False)
            agent_profile.user = agent_user
            agent_profile.save()
            
            # Generate activation link
            uid = urlsafe_base64_encode(force_bytes(agent_user.pk))
            token = default_token_generator.make_token(agent_user)
            activate_url = request.build_absolute_uri(f"/accounts/activate/{uid}/{token}/")
            
            # Get generated password from form
            generated_password = user_form.generated_password
            
            # Send activation email
            subject = 'Your Fire Detection System Agent Account'
            message = f'''Hello {agent_user.get_full_name() or agent_user.email},

Your agent account has been created for the Fire Detection System.

Account Details:
- Email: {agent_user.email}
- Password: {generated_password}

Please activate your account by clicking the link below:
{activate_url}

After activation, you can log in using the email and password provided above.

Best regards,
Fire Detection System Team'''
            
            # Debug: Print email configuration before sending
            print(f"\n=== Email Configuration Debug ===")
            print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
            print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
            print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
            print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
            print(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
            print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
            print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
            print(f"Recipient: {agent_user.email}")
            print(f"================================\n")
            
            try:
                # Use get_connection to ensure we're using the correct backend
                from django.core.mail import get_connection
                connection = get_connection()
                print(f"Using connection: {connection}")
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[agent_user.email],
                    fail_silently=False,
                    connection=connection,
                )
                messages.success(request, f'Agent {agent_user.email} created successfully! An activation email has been sent.')
            except Exception as e:
                # Log the full error for debugging
                import traceback
                error_details = traceback.format_exc()
                print(f"\n=== Email sending error ===")
                print(f"Error: {str(e)}")
                print(f"Full traceback:\n{error_details}")
                print(f"===========================\n")
                messages.error(request, f'Agent {agent_user.email} created, but failed to send activation email. Error: {str(e)}. Please check server console for details.')
            
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