from django.db import models
from accounts.models import CustomUser
from agents.models import AgentProfile

class Project(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Informations de base
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Dates (SEULEMENT start_date)
    start_date = models.DateField()  # ← CE CHAMP DOIT EXISTER
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Statut
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Relations
    supervisor = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': CustomUser.USER_TYPE_SUPERVISOR},
        related_name='supervised_projects'
    )
    
    assigned_agents = models.ManyToManyField(
        AgentProfile,
        related_name='assigned_projects',
        blank=True
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Project"
        verbose_name_plural = "Projects"