# agents/forms.py
from django import forms
from accounts.models import CustomUser
from .models import AgentProfile

class AgentCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name']
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = CustomUser.USER_TYPE_AGENT
        user.set_password(self.cleaned_data["password1"])
        
        if commit:
            user.save()
            # NE PAS créer le profil ici - ça sera fait dans la vue
        return user

class AgentProfileForm(forms.ModelForm):
    class Meta:
        model = AgentProfile
        fields = ['phone_number', 'address']