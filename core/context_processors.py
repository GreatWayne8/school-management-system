from django.contrib.auth.models import Group

def user_groups(request):
    """Returns user groups as a context variable"""
    if request.user.is_authenticated:
        return {
            'is_student': request.user.groups.filter(name="Students").exists()
        }
    return {'is_student': False}
