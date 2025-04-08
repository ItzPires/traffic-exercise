from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.conf import settings


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff


class SensorAPIOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["POST"]:
            api_key = request.headers.get("X-API-KEY")
            return api_key == settings.API_KEY_SENSOR
        return True
