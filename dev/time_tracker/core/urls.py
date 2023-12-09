from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
    path('entries/', views.list_time_entries, name='list-entries'),
    path('clock-in/', views.clock_in, name='clock_in'),
    path('clock-out/', views.clock_out, name='clock_out'),
    # Add other app-specific URLs here
]


