from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('activate/<str:uidb64>/<str:token>/', views.activate_view, name='activate'),
    # Simple dashboards for testing role-based redirects
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/supervisor/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('dashboard/agent/', views.agent_dashboard, name='agent_dashboard'),
]
