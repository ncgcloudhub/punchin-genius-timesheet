# project-level time_tracker/urls.py config
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
from core.views import CustomLoginView  # Import the custom_login view

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin site
    path('core/', include('core.urls', namespace='core')),
    path('employer/', include('employer.urls')),

    # Authentication Views
    path('employee_dashboard/', core_views.employee_dashboard,
         name='employee_dashboard'),
    path('register/', core_views.register, name='register'),
    path('accounts/login/', CustomLoginView.as_view(),
         name='login'),
    path('accounts/logout/',
         auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(
        template_name='core/password_change_form.html'), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='core/password_change_done.html'), name='password_change_done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='core/password_reset_form.html'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/password_reset_complete.html'), name='password_reset_complete'),
    path('dashboard_redirect/', core_views.dashboard_redirect,
         name='dashboard_redirect'),
    # Include the default Django authentication URLs for good measure (includes 'logout')
    path('accounts/', include('django.contrib.auth.urls')),
]
