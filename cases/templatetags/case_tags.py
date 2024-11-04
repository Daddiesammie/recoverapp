from django import template

register = template.Library()

@register.filter
def get_current_step_name(verification_steps):
    """Returns the name of the current verification step"""
    for step in verification_steps:
        if step['current']:
            return step['name']
    return ''