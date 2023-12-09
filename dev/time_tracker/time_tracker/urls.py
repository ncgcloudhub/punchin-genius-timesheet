"""
URL configuration for time_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views as core_views




# project-level urls.py config

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    #path('logout/', auth_views.LogoutView.as_view(template_name='core/logout.html'), name='logout'),
    path('register/', core_views.register, name='register'),
    path('dashboard/', core_views.dashboard, name='dashboard'),
    path('account/user_profile', core_views.user_profile, name='user_profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='core/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('login/', core_views.login_redirect, name='login_redirect'),
    # Password reset links (refers to the built-in views and forms)
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # Add other project-level URLs here
    path('core/', include('core.urls')),
]
