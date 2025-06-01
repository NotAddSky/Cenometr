from django.shortcuts import render
from django.http import HttpResponseForbidden


class AdminAccessRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and request.user.is_authenticated:
            if request.user.role != 'admin':
                return render(request, '403.html', status=403)

        return self.get_response(request)
