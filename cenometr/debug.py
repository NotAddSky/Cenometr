from django.conf import settings


def show_toolbar(request):
    return settings.DEBUG and request.user.is_authenticated and request.user.is_superuser
