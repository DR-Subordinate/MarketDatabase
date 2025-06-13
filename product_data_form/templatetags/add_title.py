from django import template

register = template.Library()

@register.filter
def add_value_as_title(field):
    """Add the field's current value as the title attribute"""
    if hasattr(field, 'value') and field.value():
        attrs = {'title': str(field.value())}
        return field.as_widget(attrs=attrs)
    return field
