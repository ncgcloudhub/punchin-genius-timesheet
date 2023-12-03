from django.urls import path
from . import views

urlpatterns = [
    path('entires/', views.list_time_entries, name='list-entries'),
]

