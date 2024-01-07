# core/templatetags/form_helpers.py

from django import template

register = template.Library()


@register.filter(name='add_classes')
def add_classes(value, arg):
    css_classes = value.field.widget.attrs.get('class', '')
    new_classes = arg.split()
    if css_classes:
        css_classes = f"{css_classes} {' '.join(new_classes)}"
    else:
        css_classes = ' '.join(new_classes)
    return value.as_widget(attrs={'class': css_classes})
