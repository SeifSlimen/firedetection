from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    path('add/', views.add_agent, name='add_agent'),
    path('list/', views.agent_list, name='agent_list'),
    path('stream_cam/<int:zone_id>', views.stream_superviseur, name='stream_cam'),
    path('video_feed/<int:cam_id>/', views.video_feed, name='video_feed'),
]