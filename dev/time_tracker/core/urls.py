# /core/urls.py  --> app specific urls

from django.urls import path
# from . import views as core_views  # Import from core.views
from .import views

app_name = 'core'

urlpatterns = [
    path('account/user_profile/', views.user_profile, name='user_profile'),
    path('entries/', views.list_time_entries, name='list-entries'),
    path('clock-in/', views.clock_in, name='clock_in'),
    path('clock-out/', views.clock_out, name='clock_out'),
    # Add other app-specific URLs here
]
