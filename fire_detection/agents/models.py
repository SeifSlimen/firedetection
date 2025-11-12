from django.db import models
from accounts.models import CustomUser

class AgentProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': CustomUser.USER_TYPE_AGENT}
    )
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    hire_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Agent: {self.user.email}"