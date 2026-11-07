from django.core.exceptions import PermissionDenied
from functools import wraps


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            
            if request.user.role in allowed_roles or request.user.is_admin:
                return view_func(request, *args, **kwargs)
            
            raise PermissionDenied("You do not have permission to access this page.")
        return _wrapped_view
    return decorator