from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    path('add/', views.add_agent, name='add_agent'),
    path('list/', views.agent_list, name='agent_list'),
]