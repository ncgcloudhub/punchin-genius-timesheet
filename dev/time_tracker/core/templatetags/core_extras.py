# /core/templatetags/core_extras.py

from django import template
from core.utils import can_access_employer_dashboard


register = template.Library()


@register.filter(name='can_access_employer_dashboard')
def can_access_employer_dashboard_filter(user):
    return can_access_employer_dashboard(user)
