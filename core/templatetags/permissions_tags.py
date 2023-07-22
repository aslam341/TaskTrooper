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

@register.simple_tag
def get_project_permission(user, project):
    project_permission = user.project_permissions.filter(project_id=project.id).first()
    if project_permission:
        return project_permission.get_permission_display()
    return "No permission found"

@register.simple_tag
def get_project_permission_level(user, project):
    project_permission = user.project_permissions.filter(project_id=project.id).first()
    if project_permission:
        return project_permission.permission_level
    return "N/A"

@register.simple_tag
def get_user_profile(user, project):
    user_profile = user.profiles.filter(project_id=project.id).first()
    if user_profile:
        return user_profile
    return "N/A"