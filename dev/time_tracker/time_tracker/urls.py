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
# Import the custom_login view
from core.views import CustomLoginView, CustomLogoutView
from django.conf import settings

# {Project Level URLs Configuration}
urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    path('register/', core_views.register, name='register'),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),
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
    path('activate/<uidb64>/<token>/', core_views.activate, name='activate'),
    path('account_activation_sent/', core_views.account_activation_sent,
         name='account_activation_sent'),
    path('user_app_settings/', core_views.user_app_settings,
         name='user_app_settings'),
    path('accounts/', include('django.contrib.auth.urls')),
]

# Conditional inclusion of employer URLs
if settings.INCLUDE_EMPLOYER_APP:
    urlpatterns += [path('employer/',
                         include('employer.urls', namespace='employer'))]
