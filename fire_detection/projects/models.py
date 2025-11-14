from django.db import models
from accounts.models import CustomUser
from agents.models import AgentProfile
from django.core.validators import MinValueValidator, MaxValueValidator

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

class Zone(models.Model):
    Zone_ID = models.AutoField(primary_key=True)
    name_zone = models.CharField(max_length=100)
    coords_polys = models.JSONField(null=True, blank=True)    
    description_zone = models.TextField(null=True, blank=True)
    name_project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='zones')

    def __str__(self):
        return f"{self.name_zone} du projet {self.name_project.name}"
# -------------- Model Cam ---------------------------
class Cam(models.Model):
    cam_ID = models.AutoField(primary_key=True)
    name_cam = models.CharField(max_length=100) 
    coords_cam = models.JSONField(null=True, blank=True)
    adresse_cam = models.GenericIPAddressField(null=True, blank=True)
    num_port = models.PositiveIntegerField(null=True,blank=True, 
    validators=[MinValueValidator(1), MaxValueValidator(65535)])
    rest_de_path = models.CharField(max_length=200, null=True, blank=True)
    description_cam = models.TextField(null=True, blank=True)
    custom_url = models.TextField(null=True, blank=True)
    is_full_rtsp_url = models.BooleanField(default=False)
    name_zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='cameras')


    def __str__(self):
        return f"{self.name_cam} (zone : {self.name_zone.name_zone}, projet : {self.name_zone.name_project.name})"
    
    @property
    def rtsp_url(self):
        """
        Génère l'URL RTSP complète de la caméra.
        Utilise custom_url si is_full_rtsp_url est True, sinon construit l'URL.
        """
        if self.is_full_rtsp_url and self.custom_url:
            return self.custom_url
        
        if self.adresse_cam and self.num_port and self.rest_de_path:
            return f"rtsp://{self.adresse_cam}:{self.num_port}/{self.rest_de_path}"
        
        return None
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.is_full_rtsp_url:
            if not self.custom_url:
                raise ValidationError({
                    'custom_url': 'Une URL personnalisée est requise.'
                })
        else:  # ← Ajouter ce else
            if not all([self.adresse_cam, self.num_port, self.rest_de_path]):
                raise ValidationError(
                    'Adresse IP, port et chemin sont requis.'
                )