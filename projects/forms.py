from django import forms
from .models import Project
from agents.models import AgentProfile

class ProjectCreationForm(forms.ModelForm):
    assigned_agents = forms.ModelMultipleChoiceField(
        queryset=AgentProfile.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign to Agents"
    )
    
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'start_date', 'assigned_agents'
            # SUPPRIMER 'priority' et 'end_date'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter project name',
                'class': 'form-control col-md-6'  # Bootstrap : largeur moitié écran md+
            }),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        self.supervisor = kwargs.pop('supervisor', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        project = super().save(commit=False)
        if self.supervisor:
            project.supervisor = self.supervisor
        
        if commit:
            project.save()
            self.save_m2m()
        
        return project