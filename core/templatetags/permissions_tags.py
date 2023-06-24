from django import template
from core.models import ProjectPermission

register = template.Library()

@register.simple_tag
def has_permission(user, permission, project_id):
    project_permission = ProjectPermission.objects.filter(
        project__id=project_id,
        project__users=user,
        user=user
    ).first()

    if project_permission:
        return project_permission.has_permission(permission)

    return False