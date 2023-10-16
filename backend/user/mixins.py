from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import UserEditPermission

class UserEditPermissionMixin:
   permission_classes = [IsAuthenticated,  UserEditPermission]

class UserListPermissionMixin:
   permission_classes = [IsAuthenticated,  IsAdminUser]
