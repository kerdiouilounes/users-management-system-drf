from rest_framework import serializers
from .models import User

class UserInlineSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name= "user-retrieve-update-destroy",
        lookup_field= "pk",
    )

    role = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    is_staff = serializers.BooleanField(write_only=True, default=False)
    is_superuser = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = User
        fields = ['pk', 'url' , 'email', 'password', 'fullname', 'is_active', 'role', 'first_name', 'last_name', 'is_staff', 'is_superuser']

    def get_role(self, obj):
        if obj.is_superuser:
            return "super-user"
        if obj.is_staff:
            return "staff-user"
        return "consumer"
    
    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'email','password', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']