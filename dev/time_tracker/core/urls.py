# /core/urls.py  --> app specific urls

from django.urls import path
# from . import views as core_views  # Import from core.views
from .import views

app_name = 'core'

urlpatterns = [
    path('account/user_profile_settings/',
         views.user_profile_settings, name='user_profile_settings'),
    path('entries/', views.list_time_entries, name='list-entries'),
    path('clock-in/', views.clock_in, name='clock_in'),
    path('clock-out/', views.clock_out, name='clock_out'),
    path('employee-dashboard/', views.employee_dashboard,
         name='employee_dashboard'),
    path('dashboard-redirect/', views.dashboard_redirect,
         name='dashboard_redirect'),
    path('apply-employer/', views.apply_employer, name='apply_employer'),
    path('test-dashboard/', views.test_dashboard, name='test_dashboard'),
    # Add other app-specific URLs here
]
