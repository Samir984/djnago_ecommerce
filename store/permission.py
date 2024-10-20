
from rest_framework import permissions

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Allow read-only (safe) methods for everyone
        if request.method in SAFE_METHODS:
            return True
        # Allow write methods only for admin (staff) users
        return bool(
            request.user and request.user.is_authenticated and request.user.is_staff
        )


class FullDjangoModelPermission(permissions.DjangoModelPermissions):
    def __init__(self)->None:
        self.perms_map["GET"] = (["%(app_label)s.view_%(model_name)s"],)
