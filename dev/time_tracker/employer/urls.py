# employer/urls.py

from django.urls import path
from . import views
from core.views import list_time_entries

app_name = 'employer'

urlpatterns = [
    #    path('register/', views.employer_registration, name='employer_registration'),
    path('register/user/', views.register_user, name='register_user'),
    path('register-emloyer/', views.register_employer_details,
         name='register_employer_details'),
    path('employer_dashboard/', views.employer_dashboard,
         name='employer_dashboard'),
    path('invitation/sent/', views.invitation_sent, name='invitation_sent'),
    path('invitation/send/', views.send_invitation, name='send_invitation'),
    path('accept-invitation/<uuid:token>/',
         views.accept_invitation, name='accept_invitation'),
    path('list-time-entries/', list_time_entries, name='list_time_entries'),
]
