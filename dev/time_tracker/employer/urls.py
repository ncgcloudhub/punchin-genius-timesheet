# employer/urls.py

from django.urls import path
from . import views
from core.views import list_time_entries
# from .views import dashboard_redirect, register_user, register_employer_details, employer_dashboard, invitation_sent, send_invitation, accept_invitation, employer_list, EmployerListView

app_name = 'employer'

urlpatterns = [
    path('dashboard-redirect/', views.dashboard_redirect,
         name='dashboard_redirect'),
    # path('register/user/', views.register_user, name='register_user'),
    path('register-employer/', views.register_employer,
         name='register_employer'),
    path('dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('invitation/sent/', views.invitation_sent, name='invitation_sent'),
    path('invitation/send/', views.send_invitation, name='send_invitation'),
    path('account_activation_sent/', views.account_activation_sent,
         name='account_activation_sent'),
    path('accept-invitation/<uuid:token>/',
         views.accept_invitation, name='accept_invitation'),
    path('employer-list/', views.employer_list, name='employer_list'),
    path('employer-list-view/', views.EmployerListView.as_view(),
         name='employer_list_view'),
    path('activate/<uidb64>/<token>/',
         views.activate_employer, name='activate_employer'),
    # Add the URL pattern for 'account_activation_sent' view
    # ...
]
