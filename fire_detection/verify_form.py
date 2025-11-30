import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fire_detection.settings')
django.setup()

from agents.models import AgentProfile
from accounts.models import CustomUser
from projects.forms import ProjectCreationForm

try:
    # Create dummy agent
    print("Creating dummy agent...")
    u = CustomUser.objects.create_user('test_agent_verify@example.com', 'password', user_type='agent')
    p = AgentProfile.objects.create(user=u)
    
    # Check form
    print("Instantiating form...")
    form = ProjectCreationForm()
    count = form.fields['assigned_agents'].queryset.count()
    print(f'Agents in form: {count}')
    
    if count >= 1:
        print("SUCCESS: Agent found in form.")
    else:
        print("FAILURE: Agent NOT found in form.")

finally:
    # Cleanup
    print("Cleaning up...")
    if 'u' in locals():
        u.delete()
