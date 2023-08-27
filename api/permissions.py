from rest_framework.permissions import BasePermission
from rest_framework import permissions

# This custom permission had to be written since this particular one is not provided by drf
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        
        return bool(request.user and request.user.is_staff)
    

# class IsAdminUserOrReadOnly(BasePermission):
#     def has_permission(self, request, view):
#         if request.method in permissions.SAFE_METHODS:
#             return True  # Allow read-only access to everyone
#         return request.user and request.user.is_staff
    

# This permission is to allow only an admin or the profile owner to access a profile
# and edit it or be able to create a new profile if it's an admin.
class IsProfileOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or (request.user.is_authenticated and request.user.is_staff)


#  Below permissions are unused
class IsProfileOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanCreateProfile(BasePermission):
    def has_permission(self, request, view):
        # Allow admin users to create profiles
        return request.user.is_staff
