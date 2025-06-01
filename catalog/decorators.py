from functools import wraps
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

ACCESS_HIERARCHY = {
    'admin': ['admin'],
    'owner': ['admin', 'owner'],
    'user': ['admin', 'owner', 'user']
}

def role_required(access_level):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in ACCESS_HIERARCHY.get(access_level, []):
                return view_func(request, *args, **kwargs)
            return render(request, '403.html', status=403)
        return _wrapped_view
    return decorator

