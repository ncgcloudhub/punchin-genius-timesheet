# core/templatetags/form_tags.py
from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(value, arg):
    css_classes = value.field.widget.attrs.get('class', '')
    if css_classes:
        css_classes = f'{css_classes} {arg}'
    else:
        css_classes = arg
    return value.as_widget(attrs={'class': css_classes, 'placeholder': ' '})


@register.filter(name='add_classes')
def add_classes(value, arg):
    css_classes = value.field.widget.attrs.get('class', '')
    if css_classes:
        css_classes = f'{css_classes} {arg}'
    else:
        css_classes = arg
    # Ensure placeholder is always set to a space for floating labels
    return value.as_widget(attrs={'class': css_classes, 'placeholder': ' '})
