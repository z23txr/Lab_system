from functools import wraps
from django.core.exceptions import PermissionDenied

def role_required(url_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if not request.user.role:
                raise PermissionDenied
            has_permission = request.user.role.page_permissions.filter(
                url_name=url_name
            ).exists()
            if not has_permission:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator