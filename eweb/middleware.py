from django.shortcuts import render
from django.conf import settings


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if settings.MAINTENANCE_MODE:
            response = render(request,'maintain.html')
            return response
        response = self.get_response(request)
        return response

