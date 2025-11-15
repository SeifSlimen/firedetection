# agents/forms.py
from django import forms
from django.utils.crypto import get_random_string
from accounts.models import CustomUser
from .models import AgentProfile

class AgentCreationForm(forms.ModelForm):
    """Form for creating agent accounts with auto-generated passwords."""
    
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = CustomUser.USER_TYPE_AGENT
        # Generate a secure random password (12 characters with letters, digits, and special chars)
        generated_password = get_random_string(length=12, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*')
        user.set_password(generated_password)
        # Store the generated password in the form instance for email sending
        self.generated_password = generated_password
        
        if commit:
            user.save()
            # NE PAS créer le profil ici - ça sera fait dans la vue
        return user

class AgentProfileForm(forms.ModelForm):
    class Meta:
        model = AgentProfile
        fields = ['phone_number', 'address']