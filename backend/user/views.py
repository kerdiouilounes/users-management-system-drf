from rest_framework import generics, status
from rest_framework.response import Response

from .permissions import StaffManageUserDjangoModelPermissions, UserCreatePermission
from .mixins import UserEditPermissionMixin, UserListPermissionMixin
from .models import User
from .serializers import UserInlineSerializer, UserDetailSerializer


class UserListCreateView(
    UserListPermissionMixin,
    generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserInlineSerializer

    def get_permissions(self):
        request =  self.request
        permissions = []
        if request.method in ['POST', 'PUT']:
            # View Action : Create
            permissions.append(UserCreatePermission())
        else:
            # View Action : List
            # see [UserListPermissionMixin]
            permissions = super().get_permissions()

        if request.user.is_staff:
            permissions.append(StaffManageUserDjangoModelPermissions())
        
        return permissions
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        # At this point user.is_staff [see UserListPermissionMixin]
        return User.objects.get_consumer_users()
    
    def perform_create(self, serializer):
        user = self.request.user
        validated_data = serializer.validated_data
        # User is not Authenticated : can register him self [as Consumer and if unique]
        if (user is None) or (user.is_anonymous):
            validated_consumer = User.objects.create_validated_consumer_data(**validated_data)
            return serializer.save(**validated_consumer)
        # User is Superuser: can register any user (Consumer, Staff, Superuser)
        if user.is_superuser:
            validated_user = User.objects.create_validated_user_data(**validated_data)
            return serializer.save(**validated_user)
        # User is Staff: can register Consumers only
        if user.is_staff:
            validated_consumer = User.objects.create_validated_consumer_data(**validated_data)
            return serializer.save(**validated_consumer)
        # Note : Case of Authenticated Consumer : can't register anything,
        # PermissionDenied will be raised see[UserCreatePermission]

class UserRetrieveUpdateDestroyView(
    UserEditPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def get_permissions(self):
        request =  self.request
        #see [UserEditPermissionMixin]
        permissions = super().get_permissions()
        if request.user.is_staff:
            user_to_read_or_edit_pk = self.kwargs.get(self.lookup_field)
            # If staff tries to_read_or_edit him self (request.user == user_to_read_or_edit),
            # skipp StaffManageUserDjangoModelPermissions. else check permissions
            if request.user.pk != user_to_read_or_edit_pk:
                permissions.append(StaffManageUserDjangoModelPermissions())
        
        return permissions
    

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        return Response("User deleted successfully", status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        user = self.request.user
        validated_data = serializer.validated_data
        # User is Superuser: can update any user (Consumer, Staff, Superuser)
        if user.is_superuser:
            validated_user = User.objects.create_validated_user_data(**validated_data)
            return serializer.save(**validated_user)
        # Case of Staff : can update him self and any Consumer [see UserEditPermissionMixin]
        # Case of Consumer : can update him self only [see UserEditPermissionMixin]
        validated_consumer = User.objects.create_validated_consumer_data(**validated_data)
        return serializer.save(**validated_consumer)


class UserSelfRetrieveView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def get_object(self):
        user = self.request.user
        return user
    