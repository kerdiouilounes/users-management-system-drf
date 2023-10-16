from rest_framework import permissions
from api.permissions import CustomDjangoModelPermissions

class UserEditPermission(permissions.BasePermission):
    
    def has_permission(self, request, view):
        user = request.user
        user_to_read_or_edit = view.get_object()
        # User (Consumer, Staff, Superuser) tries to retrieve, update, delete him self: Has Permission
        if user == user_to_read_or_edit:
            return True
        # Superuser tries to retrieve, update, delete Any user (Consumer, Staff, Superuser) : Has Permission
        if user.is_superuser:
            return True
        # Staff tries to retrieve, update, delete Consumer : Has Permission
        if user.is_staff and user_to_read_or_edit.is_consumer:
            return True
        # If Forbidden action is used on Forbidden User : Doesn't Have Permission
        return False

class UserListPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        # Superuser and Staff Have Permission to list users:
        # Superuser can list all users (Consumer, Staff, Superuser)
        # Staff can list only Consumers [handled in ListView.get_queryset()]
        if user.is_superuser or user.is_staff:
            return True
        return False
    
class UserCreatePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        # Only authenticated consumer that does not have permission to create new user
        if user is None or user.is_anonymous or user.is_superuser or user.is_staff:
            return True
        return False
    
class StaffManageUserDjangoModelPermissions(CustomDjangoModelPermissions):
    pass