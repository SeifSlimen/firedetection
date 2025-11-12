# projects/urls.py
from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('create/', views.create_project, name='create_project'),
    path('add_zone/<int:project_id>', views.add_zone, name='add_zone'),
    path('add_cam/<str:name_zone>', views.add_cam, name='add_cam'),

    path('list/', views.project_list, name='project_list'),
    path('<int:project_id>/', views.project_detail, name='project_detail'),
    path('<int:project_id>/delete/', views.delete_project, name='delete_project'),

]